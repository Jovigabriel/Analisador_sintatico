class TesteRecuperacao inherits Object {

    metodo_quebrado(x : Int) : Int {
        if x < 10
            x + 1
        fi
    };

    metodo_correto(a : Int, b : Int) : Int {
        a + b
    };

    outro_correto() : Bool {
        true
    };
};