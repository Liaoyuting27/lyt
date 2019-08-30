package com.fiberhome.jpatest.repository;

import com.fiberhome.jpatest.entity.student;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface studentRepository extends JpaRepository<student,Integer> {
    @Query("select u from student u where u.name like %?1%")
    List<student> findByNameLike(String name);
}
