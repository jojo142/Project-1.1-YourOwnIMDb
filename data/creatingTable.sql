CREATE OR REPLACE TABLE MotionPicture (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    rating DECIMAL(3, 1) CHECK (10 >= rating >= 0),
    production VARCHAR(255),
    budget BIGINT CHECK (budget > 0)
);

CREATE OR REPLACE TABLE User (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    age INT
);

CREATE OR REPLACE TABLE Likes (
    mpid INT,
    uemail VARCHAR(255),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
    FOREIGN KEY (uemail) REFERENCES User(email) ON DELETE CASCADE,
    PRIMARY KEY (mpid, uemail)
);

CREATE OR REPLACE TABLE Movie (
    mpid INT,
    boxoffice_collection FLOAT CHECK (boxoffice_collection >= 0),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE

);

CREATE or REPLACE TABLE Series (
    mpid INT,
    season_count INT CHECK (season_count >= 1),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE
);

CREATE OR REPLACE TABLE People (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    nationality VARCHAR(255),
    dob DATE,
    gender CHAR(1)
);

CREATE OR REPLACE TABLE Role (
    mpid INT,
    pid INT,
    role_name VARCHAR(255),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
    FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE,
    PRIMARY KEY (mpid, pid, role_name)
);

CREATE OR REPLACE TABLE Award (
    mpid INT,
    pid INT,
    award_name VARCHAR(255),
    award_year INT,
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
    FOREIGN KEY (pid) REFERENCES People(id) ON DELETE CASCADE,
    PRIMARY KEY (mpid, pid, award_name, award_year)
);

CREATE OR REPLACE TABLE Genre (
    mpid INT,
    genre_name VARCHAR(255),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
    PRIMARY KEY (mpid, genre_name)
);

CREATE OR REPLACE TABLE Location (
    mpid INT NOT NULL,
    zip INT,
    city VARCHAR(255),
    country VARCHAR(255),
    FOREIGN KEY (mpid) REFERENCES MotionPicture(id) ON DELETE CASCADE,
    PRIMARY KEY (mpid, zip)
);