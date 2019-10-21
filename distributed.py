import math
import tempfile
import time
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data


flags = tf.app.flags
flags.DEFINE_string("data_dir","/root/mnist/mnist-data",
                    "Directory for storing mnist data")
flags.DEFINE_integer("hidden_units",100, "Number of units in the hidden layer of the NN")
flags.DEFINE_integer("train_steps",10000,
                     "Number of (global) training steps to perform")
flags.DEFINE_integer("batch_size",100, "Training batch size")
flags.DEFINE_float("learning_rate",0.01, "Learning rate")
flags.DEFINE_boolean("sync_replicas",False, "True or False")
flags.DEFINE_integer("replicas_to_aggregate",None,"Number") #多少batch更新一次
#定义ps的地址
flags.DEFINE_string("ps_hosts","192.168.122.223:2222","hostname:port")
flags.DEFINE_string("worker_hosts","192.168.122.3:2222, 192.168.122.5:2222","hostname:port")
flags.DEFINE_string("job_name",None, "job name: worker or ps")
flags.DEFINE_integer("task_index",None, "worker task index")

FLAGS = flags.FLAGS
IMAGE_PIXELS = 28



def main(unused_argv):
    mnist = input_data.read_data_sets(FLAGS.data_dir,one_hot = True)
    
    #检测命令行输入的参数，确保有job_name和task_index这两个必备参数
    if FLAGS.job_name is None or FLAGS.job_name == "":
        raise ValueError("Must specify an explicit 'job_name'")
    if FLAGS.task_index is None or FLAGS.task_index == "":
        raise ValueError("Must specify an explicit 'task_index'")
        
    print("job name = %s" % FLAGS.job_name)
    print("task index = %d" % FLAGS.task_index)
    
    ps_spec = FLAGS.ps_hosts.split(",")
    worker_spec = FLAGS.worker_hosts.split(",")

    num_works = len(worker_spec)
    cluster = tf.train.ClusterSpec({"ps":ps_spec,"worker":worker_spec})
    server = tf.train.Server(cluster,job_name = FLAGS.job_name,task_index=FLAGS.task_index)
    if FLAGS.job_name == "ps":
        server.join()
        
    is_chief = (FLAGS.task_index==0)
    
    worker_device = "/job:worker/task:%d/cpu:0" % FLAGS.task_index
    #worker_device计算资源；ps_device存储模型参数资源;tf.device指定模型具体运行设备
    with tf.device(
            tf.train.replica_device_setter(
                    worker_device=worker_device,
                    ps_device = "/job:ps/cpu:0",
                    cluster = cluster)):
        global_step = tf.Variable(0,name="global_step",trainable = False)
        #记录全局训练步数
        
        hid_w = tf.Variable(
            tf.truncated_normal([IMAGE_PIXELS*IMAGE_PIXELS,FLAGS.hidden_units],
                                stddev = 1.0 / IMAGE_PIXELS),
                                name = "hid_w")
        hid_b = tf.Variable(tf.zeros([FLAGS.hidden_units]),
                        name = "hid_b")        
        sm_w = tf.Variable(
            tf.truncated_normal([FLAGS.hidden_units,10],
                                stddev = 1.0 / math.sqrt(FLAGS.hidden_units)),
                                name = "sm_w")
        sm_b = tf.Variable(tf.zeros([10]),name="sm_b")
    
        x = tf.placeholder(tf.float32,[None, IMAGE_PIXELS * IMAGE_PIXELS])
        y_ = tf.placeholder(tf.float32,[None, 10])
    
        hid_lin = tf.nn.xw_plus_b(x,hid_w,hid_b)
        hid = tf.nn.relu(hid_lin)
    
        y = tf.nn.softmax(tf.nn.xw_plus_b(hid,sm_w,sm_b))
        cross_entropy = -tf.reduce_sum(y_ * tf.log(tf.clip_by_value(y,1e-10,1.0)))
    
        opt = tf.train.AdamOptimizer(FLAGS.learning_rate)
    
    #判断是否设置了同步训练模式sync_replicas,获取所需的副本数
    #使用tf.train.SyncReplicasOptimizer创建同步训练的优化器
        if FLAGS.sync_replicas:
            if FLAGS.replicas_to_aggregate is None:
                replicas_to_aggregate = num_workers
            else:
                replicas_to_aggregate = FLAGS.replicas_to_aggregate
        
        opt = tf.train.SyncReplicasOptimizer(
                opt,
                replicas_to_aggregate=replicas_to_aggregate,
                total_num_replicas = num_workers,
                replicas_id = FLAGS.task_index,
                name = "mnist_sync_replicas")
    
        train_step = opt.minimize(cross_entropy, global_step=global_step)
    
        if FLAGS.sync_replicas and is_chief:
            chief_queue_runner = opt.get_chief_queue_runner() #创建队列执行器
            init_tokens_op = opt.get_init_tokens_op() #创建全局参数初始化器
        
        init_op = tf.global_variables_initializer()
        train_dir = tempfile.mkdtemp()
    #创建分布式监督器
        sv = tf.train.Supervisor(is_chief = is_chief,
                             logdir = logdir, #用来保存模型
                             init_op = init-op,
                             recovery_wait_secs = 1,
                             global_step = global_step)
    
    #配置参数
        sess_config = tf.ConfigProto(
            allow_soft_placement = True,
            log_device_placement = False,
            device_filters = ["/job:ps",
                              "/job:worker/task:%d" % FLAGS.task_index])
    
        if is_chief:
            print("worker %d :Initializing session ..." % FLAGS.task_index)
        else:
            print("worker %d: Waiting for session to be initialized..."
              % FLAGS.task_index)
    
        sess = sv.prepare_or_wait_for_session(server.target,config=sess_config)
    
        print("worker %d :session initialization cpmplete." %FLAGS.task_index)
    
        if FLAGS.sync_replicas and is_chief:
            print("Starting chief queue runner and running init_tokens_op")
            sv.start_queue_runners(sess,[chief_queue_runner])
            sess.run(init_tokens_op)
        
        time_begin = time.time()
        print("Training begins @ %f" % time_begin)
    
        local_step = 0
        while True:
            batch_xs, batch_ys = mnist.train.next_batch(FLAGS.batch_size)
            train_feed = {x:batch_xs, y:batch_ys}
            _, step = sess.run([train_step, global_step], feed_dict = train_feed)
            local_step += 1
            now = time.time()
            print("%f: Worker %d: training step %d done (global step: %d)" %
                  (now, FLAGS.task_index, local_step, step))
        
            if step >= FLAGS.train_steps:
                break
    
        time_end = time.time()
        print("Training ends @ %f" % time_end)
        training_time = time_end - time_begin
    
        val_feed = {x:mnist.validation.images, y_:mnist.validation.labels}
        val_xent = sess.run(cross_entropy, feed_dict = val_feed)
        print("After %d training step(s), validation cross entropy = %g" %
              (FLAGS.train_steps, val_xent))    
    
if __name__ == "__main__":
    tf.app.run()
    
    
    