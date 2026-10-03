-- Rodar uma vez no Postgres compartilhado (via pgweb ou psql)

CREATE TABLE historico_processamento (
    id SERIAL PRIMARY KEY,
    ip_origem VARCHAR(45) NOT NULL,
    processado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    quantidade_notas INTEGER,
    status VARCHAR(20) DEFAULT 'sucesso'
);

CREATE INDEX idx_historico_ip ON historico_processamento(ip_origem);
CREATE INDEX idx_historico_data ON historico_processamento(processado_em);
