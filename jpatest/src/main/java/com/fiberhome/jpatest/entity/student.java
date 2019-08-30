package com.fiberhome.jpatest.entity;
import com.sun.javafx.beans.IDProperty;

import javax.persistence.*;

@Entity
@Table(name = "student")
public class student {
    @Id
    @GeneratedValue
    private Integer id;

    @Column(name = "name")
    private String name;

    @Column(name = "age")
    private Integer age;

    @Column(name = "classroom")
    private Integer classroom;

    public student(){ }


    public Integer getId(){
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName(){
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
    public Integer getAge(){
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public Integer getClassroom(){
        return classroom;
    }

    public void setClassroom(Integer classroom){
        this.classroom = classroom;
    }


}
