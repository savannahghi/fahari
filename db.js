const { Client } = require("pg");

const pgclient = new Client({
    host: process.env.POSTGRES_HOST,
    port: process.env.POSTGRES_PORT,
    user: "postgres",
    password: "postgres",
    database: "postgres",
});

pgclient.connect();

const dropdb = "DROP DATABASE IF EXISTS mle";
const createdb = "CREATE DATABASE mle";

pgclient.query(dropdb, (err, res) => {
    if (err) throw err;
});

pgclient.query(createdb, (err, res) => {
    if (err) throw err;
});
