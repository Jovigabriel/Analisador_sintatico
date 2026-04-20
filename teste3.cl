class TesteErros inherits Object {
    metodo() : Object {
        let
            x : Int <- 10,
            s : String <- "string nao fechada
        in
            x + 1
    };

    outro() : Int {
        let y : Int <- 5 in
            y # caractere invalido
    };
};