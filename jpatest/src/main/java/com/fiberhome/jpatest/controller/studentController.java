package com.fiberhome.jpatest.controller;

import com.fiberhome.jpatest.entity.student;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/student")
public class studentController {
    @Autowired  //对类成员变量、方法及构造函数进行标注，完成自动装配的工作
    private com.fiberhome.jpatest.repository.studentRepository studentRepository;


    //查询全部信息
    @GetMapping(value = "/queryAll")
    @ResponseBody
    public List<student> queryAll(){
        List<student> list = new ArrayList<student>();
        list = studentRepository.findAll();
        return list;
    }

    //通过id查询学生信息
    @GetMapping(value = "/{id}")
    public student findById(@PathVariable("id") Integer id){
        return studentRepository.findById(id).orElse(null);
    }

    //增加学生信息
    @PostMapping("/add")
    public student addStudent(@RequestParam("name") String name,
                   @RequestParam("age") Integer age,
                   @RequestParam("classroom") Integer classroom){
        student user = new student();
        user.setName(name);
        user.setAge(age);
        user.setClassroom(classroom);
        return studentRepository.save(user);
    }

    //更新学生信息
    @PutMapping(value = "/update/{id}")
    public student updateStudent(@PathVariable("id") Integer id,
                   @RequestParam("name") String name,
                   @RequestParam("age") Integer age,
                   @RequestParam ("classroom") Integer classroom){
        student user = new student();
        user.setId(id);
        user.setName(name);
        user.setAge(age);
        user.setClassroom(classroom);
        return studentRepository.save(user);
    }

    //删除学生信息
    @DeleteMapping("/delete/{id}")
    public void deleteStudent(@PathVariable("id") Integer id){
        studentRepository.deleteById(id);
        System.out.println("success delete!");
    }

    //Like子句查询
    @GetMapping(value = "/like/{name}")
    public List<student> findByNameLike(@PathVariable("name") String name){
        return studentRepository.findByNameLike("%"+name+"%"); //注意一定要加2个%作为通配符
    }

}
