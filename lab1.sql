
CREATE TABLE "User"(
    userId INT GENERATED DEFAULT AS IDENTITY PRIMARY KEY,
    fullName VARCHAR(255) NOT NULL,
);

CREATE TABLE Friendship(
    userIdA INT,
    userIdB INT,
    PRIMARY KEY(userIdA, userIdB),
    FOREIGN KEY(userIdA) REFERENCES "User"(userId)
    FOREIGN KEY(userIdB) REFERENCES "User"(userId)
);

CREATE TABLE Subscription(
    subscriptionId INT GENERATED DEFAULT AS IDENTITY PRIMARY KEY,
    userId INT NOT NULL,
    paymentDate TIMESTAMP NOT NULL,
    paymentMethod VARCHAR(10) NOT NULL,
    FOREIGN KEY(userId) REFERENCES "User"(userId)
);

CREATE TABLE Post(
    postId INT GENERATED DEFAULT AS IDENTITY PRIMARY KEY
        CHECK(postId > 0),
    userId INT NOT NULL,
    title VARCHAR(255), -- allowed to be null
    date TIMESTAMP NOT NULL,
    place VARCHAR(255), -- allowed to be null
    FOREIGN KEY(userId) REFERENCES "User"(userId),
);

CREATE TABLE VideoPost(
    postId INT PRIMARY KEY,
    videoURL VARCHAR(2048) NOT NULL,
    codec VARCHAR(255) NOT NULL,
    FOREIGN KEY(postId) REFERENCES Post(postId)
);

CREATE TABLE ImagePost(
    postId INT PRIMARY KEY,
    imageURL VARCHAR(2048) NOT NULL,
    filter VARCHAR(255), -- allowed to be null
    FOREIGN KEY(postId) REFERENCES Post(postId)
);

CREATE TABLE TextPost(
    postId INT PRIMARY KEY,
    textContent TEXT NOT NULL,
    FOREIGN KEY(postId) REFERENCES Post(postId)
);

CREATE TABLE PostTags(
    postId INT,
    tag VARCHAR(255)
        CHECK(tag IN ('crypto', 'studying', 'question', 'social')),
    PRIMARY KEY(postId, tag),
    FOREIGN KEY(postId) REFERENCES Post(postId),
);

CREATE TABLE "Like"(
    postId INT,
    userId INT,
    timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY(postId, userId),
    FOREIGN KEY(postId) REFERENCES Post(postId),
    FOREIGN KEY(userId) REFERENCES "User"(userId)
);

CREATE TABLE Event(
    eventId INT GENERATED DEFAULT AS IDENTITY PRIMARY KEY,
    userId INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    place VARCHAR(255) NOT NULL,
    startDate DATE NOT NULL,
    endDate DATE NOT NULL,
    CHECK(startDate <= endDate)
)