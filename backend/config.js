var userName = "postgres",
    userPass = "postgres",
    dbHost = "localhost",
    dbPort = 5431,
    dbName = "postgres",
    ssl = false;

module.exports = {
    getDBAuth: function () {
        return "postgres://" + userName + ":" + userPass + "@" + dbHost + ":" + dbPort + "/" + dbName + "?ssl=" + ssl;
    },
};