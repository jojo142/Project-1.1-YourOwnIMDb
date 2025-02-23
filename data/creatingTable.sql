CREATE TABLE MotionPicture (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    rating DECIMAL(3, 1),
    production VARCHAR(255),
    budget INT
);

CREATE TABLE Users (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    age INT
);

CREATE TABLE Likes (
    mpid INT,
    uemail VARCHAR(255),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id),
    FOREIGN KEY (uemail) REFERENCES Users(email),
    PRIMARY KEY (mpid, uemail)
);

CREATE TABLE Movie (
    mpid INT,
    boxoffice_collection INT,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
);

CREATE TABLE Series (
    mpid INT,
    season_count INT,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id)
);

CREATE TABLE People (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    nationality VARCHAR(255),
    dob DATE,
    gender CHAR(1)
);

CREATE TABLE Role (
    mpid INT,
    pid INT,
    role_name VARCHAR(255),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id),
    FOREIGN KEY (pid) REFERENCES People(id),
    PRIMARY KEY (mpid, pid)
);

CREATE TABLE Award (
    mpid INT,
    pid INT,
    award_name VARCHAR(255),
    award_year INT,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id),
    FOREIGN KEY (pid) REFERENCES People(id),
    PRIMARY KEY (mpid, pid, award_name)
);

CREATE TABLE Genre (
    mpid INT,
    genre_name VARCHAR(255),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id),
    PRIMARY KEY (mpid, genre_name)
);

CREATE TABLE Location (
    mpid INT,
    zip INT,
    city VARCHAR(255),
    country VARCHAR(255),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id),
    PRIMARY KEY (mpid, zip)
);
