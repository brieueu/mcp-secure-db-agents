# Arquitetura

A arquitetura separa geração de intenção/SQL, autorização, execução e auditoria. O agente Python usa o modelo local para propor uma consulta, mas a execução passa por ferramentas MCP. A ferramenta `executar_consulta_segura` valida sintaxe e tipo de comando, aplica política por papel, audita a decisão e só então executa com usuário read-only.
