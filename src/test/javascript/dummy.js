var dummy = function() {
    return "hello";
}

var err = function() {
    throw new Error("oh no, an error!");
}

var notdummy = function() {
    return "world";
}

module.exports = {
    dummy: dummy,
    err: err,
    notdummy: notdummy
}