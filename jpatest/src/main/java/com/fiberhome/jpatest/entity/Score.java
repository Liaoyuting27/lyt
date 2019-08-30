package com.fiberhome.jpatest.entity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "Score")
public class Score {
    @Id
    @Column(name = "scoreId")
    private Integer scoreId;

    @Column(name = "math")
    private Integer math;

    @Column(name = "english")
    private Integer english;

    @Column(name = "chinese")
    private Integer chinese;

    private Integer id;

    public Integer getScoreId() {
        return scoreId;
    }

    public void setScoreId(Integer ScoreId) {
        this.scoreId = scoreId;
    }

    public Integer getMath() {
        return math;
    }

    public void setMath(Integer math) {
        this.math = math;
    }

    public Integer getEnglish() {
        return english;
    }

    public void setEnglish(Integer english) {
        this.english = english;
    }

    public Integer getChinese() {
        return chinese;
    }

    public void setChinese(Integer chinese) {
        this.chinese = chinese;
    }
}
