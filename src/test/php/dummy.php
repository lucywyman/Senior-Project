<?php

function dummy() {
    return "hello";
}

function err() {
    $error = 'Always throw this error';
    throw new Exception($error);
}

function notdummy() {
    return "world";
}

?>