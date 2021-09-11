DROP TABLE IF EXISTS senhas;

CREATE TABLE senhas (
    url_link TEXT NOT NULL PRIMARY KEY,
    Data_criacao DATE NOT NULL DEFAULT CURRENT_DATE,
    Acessos_disponiveis  NUMERIC NOT NULL,
    Acessos_realizados NUMERIC NOT NULL,
    Data_expiracao TIMESTAMP NOT NULL,
    senha TEXT NOT NULL
);