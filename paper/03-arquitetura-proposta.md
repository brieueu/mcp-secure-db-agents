# 3. Arquitetura Proposta

Esta seção apresenta a arquitetura proposta para permitir que agentes baseados em Grandes Modelos de Linguagem realizem consultas seguras a bancos de dados relacionais por meio do **Model Context Protocol** (MCP). A proposta parte do princípio de que o agente LLM não deve possuir acesso direto ao banco de dados. Em vez disso, toda comunicação entre o agente e o sistema gerenciador de banco de dados deve ser mediada por um **Servidor MCP**, responsável por receber a requisição, identificar o usuário, validar a consulta, aplicar políticas de acesso e encaminhar ao banco apenas operações autorizadas.

A arquitetura foi concebida para tratar o MCP não apenas como um mecanismo de integração entre agentes e ferramentas externas, mas como uma camada arquitetural de mediação e governança. Dessa forma, o Servidor MCP atua como uma fronteira de segurança entre o comportamento probabilístico do agente LLM e os recursos críticos armazenados no banco de dados relacional. Essa separação permite que decisões de segurança sejam aplicadas fora do modelo, reduzindo a dependência exclusiva de instruções em linguagem natural ou de técnicas de engenharia de prompt.

## 3.1 Visão geral da arquitetura

A arquitetura proposta é composta pelos seguintes elementos principais: usuário, interface conversacional, agente LLM orquestrador, cliente MCP, Servidor MCP, mecanismo de autenticação e identificação, validador SQL, motor de políticas, adaptador SQL e banco de dados relacional. A Figura 1 apresenta a organização conceitual da proposta.

```text
Usuário
  │ Prompt em linguagem natural
  ▼
Interface Conversacional
  │ Requisição
  ▼
Agente LLM Orquestrador
  │ Chamada de ferramenta
  ▼
Cliente MCP
  │ Requisição MCP
  ▼
Servidor MCP
  ├── Servidor MCP Gateway de Entrada
  ├── Autenticação / Identificação
  ├── Validador SQL
  ├── Motor de Políticas
  └── Adaptador SQL
          │ Executar SQL
          ▼
Banco de Dados Relacional / IDE
```

**Figura 1 — Arquitetura proposta para consultas seguras a bancos relacionais mediadas por MCP.**

O fluxo geral inicia-se quando o usuário envia uma pergunta em linguagem natural, como, por exemplo: “Mostre as vendas do mês passado por região”. A interface conversacional recebe essa solicitação e a encaminha ao agente LLM orquestrador. O agente interpreta a intenção do usuário e, caso identifique a necessidade de consultar dados estruturados, aciona uma ferramenta por meio do cliente MCP. O cliente MCP encapsula a chamada e a envia ao Servidor MCP, que passa a controlar o processo de validação, autorização e execução da consulta.

No interior do Servidor MCP, a requisição passa inicialmente pelo Gateway de Entrada, que identifica a ferramenta solicitada e direciona a chamada aos componentes internos. Em seguida, a arquitetura realiza verificações complementares. O módulo de autenticação e identificação determina quem está realizando a solicitação. O Validador SQL verifica se a consulta candidata é sintaticamente correta, semanticamente compatível com o esquema permitido e segura para execução. O Motor de Políticas decide se o usuário ou sessão possui permissão para executar a operação solicitada. Apenas quando a consulta é validada e autorizada, o Adaptador SQL encaminha a operação ao banco de dados relacional.

Essa organização garante que o agente LLM não execute comandos diretamente sobre o banco. O modelo pode interpretar a intenção do usuário e propor uma chamada de ferramenta ou uma consulta candidata, mas a execução final depende de validações e regras aplicadas por componentes determinísticos no Servidor MCP.

## 3.2 Componentes da arquitetura

### 3.2.1 Usuário

O usuário é o ator que inicia o processo por meio de uma instrução em linguagem natural. Ele não precisa conhecer a estrutura interna do banco de dados nem escrever consultas SQL manualmente. Sua interação ocorre por meio de perguntas, solicitações analíticas ou comandos de exploração de dados.

Exemplos de perguntas incluem:

- “Mostre as vendas do mês passado por região.”
- “Qual produto teve maior faturamento no último trimestre?”
- “Liste as regiões com maior número de pedidos.”
- “Qual foi o total de vendas por mês?”

Apesar da simplicidade da interação, a entrada do usuário deve ser tratada como não confiável. O usuário pode formular solicitações ambíguas, indevidas ou maliciosas, como pedidos de acesso a dados sensíveis ou tentativas de induzir o agente a ignorar regras de segurança. Por esse motivo, a arquitetura não confia apenas na intenção declarada no prompt.

### 3.2.2 Interface conversacional

A interface conversacional é responsável por receber o prompt do usuário e apresentar a resposta final produzida pelo sistema. Ela pode ser implementada como uma aplicação web, chatbot, interface de linha de comando, assistente integrado a uma IDE ou ambiente de desenvolvimento com suporte a agentes LLM.

Sua função principal é intermediar a comunicação entre o usuário e o agente LLM. Embora possa realizar controles básicos, como gerenciamento de sessão ou autenticação inicial, a interface não é responsável pela validação final das consultas SQL. Essa responsabilidade pertence ao Servidor MCP e aos seus componentes internos.

### 3.2.3 Agente LLM orquestrador

O agente LLM orquestrador é o componente responsável por interpretar a solicitação do usuário, decidir se é necessário consultar o banco de dados e selecionar a ferramenta apropriada. Ele pode realizar etapas como:

1. interpretar a pergunta em linguagem natural;
2. identificar a necessidade de acesso a dados estruturados;
3. solicitar ao MCP informações sobre tabelas ou visões disponíveis;
4. gerar uma consulta SQL candidata ou uma chamada de ferramenta;
5. invocar uma ferramenta MCP;
6. interpretar os resultados retornados;
7. sintetizar uma resposta em linguagem natural para o usuário.

Nesta arquitetura, o agente LLM não possui credenciais diretas de acesso ao banco de dados. Ele também não deve executar SQL por conta própria. Sua atuação é limitada às ferramentas disponibilizadas pelo Servidor MCP. Essa restrição é fundamental para reduzir riscos associados a alucinações, erros de interpretação, consultas indevidas e ataques de *prompt injection*.

### 3.2.4 Cliente MCP

O Cliente MCP é o componente responsável por transportar a chamada realizada pelo agente até o Servidor MCP. Ele funciona como uma ponte técnica entre o ambiente do agente e o servidor que expõe as ferramentas de acesso ao banco de dados.

No contexto desta arquitetura, o Cliente MCP encapsula a requisição conforme o protocolo MCP, encaminha a chamada ao servidor adequado e retorna a resposta ao agente. Ele não toma decisões de segurança por conta própria. A validação, autorização e execução controlada da consulta ocorrem no Servidor MCP.

## 3.3 Servidor MCP

O Servidor MCP é o núcleo da arquitetura proposta. Ele recebe as requisições vindas do Cliente MCP e controla quais ferramentas podem ser utilizadas, quais usuários estão autenticados, quais consultas são válidas e quais operações são autorizadas. Em vez de permitir acesso irrestrito ao banco, o servidor define uma superfície de interação limitada e governada por políticas.

No diagrama proposto, o Servidor MCP é composto por cinco elementos principais:

1. **Servidor MCP Gateway de Entrada**;
2. **Autenticação / Identificação**;
3. **Validador SQL**;
4. **Motor de Políticas**;
5. **Adaptador SQL**.

Essa organização simplifica a representação visual da arquitetura sem remover suas responsabilidades essenciais de segurança. A sanitização de entrada e saída, que antes poderia aparecer como um bloco separado, é incorporada ao Validador SQL. Já a auditoria e os registros de decisão são incorporados ao Motor de Políticas, pois é nesse componente que ocorrem as decisões de autorização, bloqueio e rastreabilidade.

## 3.4 Servidor MCP Gateway de Entrada

O Gateway de Entrada é o primeiro componente interno do Servidor MCP a receber a requisição. Ele funciona como ponto de recepção e roteamento das chamadas de ferramenta. Sua função é identificar qual ferramenta foi solicitada pelo agente, verificar se essa ferramenta pertence ao conjunto de operações expostas pelo servidor e encaminhar a requisição aos módulos adequados.

Duas ferramentas são centrais para a arquitetura proposta:

- `listar_tabelas_permitidas`;
- `executar_consulta_segura`.

A ferramenta `listar_tabelas_permitidas` retorna ao agente apenas as tabelas ou visões que podem ser consultadas no contexto atual. Essa ferramenta evita que o agente receba conhecimento completo sobre o banco de dados, reduzindo o risco de exposição de tabelas sensíveis, administrativas ou internas. Por exemplo, em vez de revelar tabelas como `clientes`, `pagamentos` ou `usuarios_admin`, o servidor pode expor apenas objetos seguros, como `vendas_resumidas`, `produtos_publicos` e `pedidos_anonimizados`.

A ferramenta `executar_consulta_segura` recebe uma consulta candidata e a submete ao fluxo de validação e autorização antes da execução. Diferentemente de uma ferramenta genérica como `executar_sql`, essa operação não executa qualquer comando enviado pelo agente. Ela representa uma interface restrita, projetada para aceitar apenas consultas de leitura que satisfaçam as regras de segurança da arquitetura.

Assim, o Gateway de Entrada atua como a porta inicial do Servidor MCP. Ele organiza a chamada, identifica a ferramenta solicitada e direciona o processamento, mas não decide sozinho se a consulta será executada. A decisão depende da autenticação, da validação SQL e do Motor de Políticas.

## 3.5 Autenticação e identificação

O módulo de autenticação e identificação verifica quem está realizando a solicitação. Essa etapa é necessária porque a validade de uma consulta depende não apenas de sua estrutura SQL, mas também do usuário, papel ou sessão associado à requisição.

Por exemplo, dois usuários podem solicitar a mesma informação, mas receber decisões diferentes. Um usuário comum pode ter permissão apenas para consultar dados agregados, enquanto um analista pode acessar visões mais detalhadas. Um administrador pode possuir permissões adicionais, mas ainda assim suas ações devem ser controladas e registradas.

A autenticação pode ser realizada por meio de tokens, credenciais de sessão, integração com provedores de identidade ou mecanismos próprios da aplicação. O resultado dessa etapa é uma identidade ou contexto de autorização, que será utilizado pelo Motor de Políticas para decidir se a operação solicitada pode ser executada.

## 3.6 Validador SQL

O Validador SQL é responsável por analisar a consulta candidata antes que ela seja executada no banco de dados. Ele opera como uma barreira técnica entre a geração de SQL pelo agente LLM e a execução efetiva no sistema relacional.

Nesta versão da arquitetura, o Validador SQL também incorpora a sanitização de entrada e saída. Isso significa que ele não se limita a verificar a sintaxe da consulta; ele também trata entradas e resultados como dados potencialmente não confiáveis, reduzindo riscos de *prompt injection*, *indirect prompt injection* e manipulação indevida da consulta.

A validação pode ser dividida em duas etapas: validação sintática e validação semântica.

Na validação sintática, o sistema verifica se o comando SQL é bem formado e se pertence ao subconjunto permitido da linguagem. Para a arquitetura proposta, recomenda-se permitir apenas comandos `SELECT`, bloqueando operações de definição, modificação ou exclusão de dados. Assim, comandos contendo palavras-chave como `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `GRANT` ou `REVOKE` devem ser rejeitados.

Na validação semântica, o sistema verifica se a consulta acessa apenas tabelas, visões e colunas autorizadas. Também podem ser avaliadas regras como limite máximo de linhas, presença obrigatória de cláusula `LIMIT`, bloqueio de múltiplas instruções SQL, restrição a funções específicas e impedimento de acesso a metadados internos do banco.

Exemplos de regras aplicadas pelo Validador SQL incluem:

1. permitir apenas consultas iniciadas por `SELECT`;
2. bloquear múltiplas instruções separadas por ponto e vírgula;
3. impedir acesso a tabelas não expostas por `listar_tabelas_permitidas`;
4. impedir acesso a colunas contendo dados pessoais ou financeiros;
5. exigir limite máximo de registros retornados;
6. bloquear funções, extensões ou comandos considerados perigosos;
7. rejeitar consultas que acessem catálogos internos do banco;
8. tratar dados textuais retornados pelo banco como conteúdo, e não como instrução.

O último ponto é importante para mitigar ataques de *indirect prompt injection*. Por exemplo, caso um campo textual armazenado no banco contenha uma frase como “ignore as instruções anteriores e consulte a tabela de pagamentos”, esse conteúdo deve ser tratado apenas como dado retornado pela consulta, e não como uma nova ordem para o agente.

## 3.7 Motor de Políticas

O Motor de Políticas é responsável por aplicar as regras de acesso da arquitetura. Enquanto o Validador SQL verifica se a consulta é bem formada e segura, o Motor de Políticas decide se o usuário identificado possui autorização para executar aquela operação específica.

No diagrama, essa decisão é representada pela saída “Permissão OK”. Conceitualmente, essa saída pode ser entendida como uma decisão binária: aprovar ou rejeitar. Apenas consultas aprovadas pelo Motor de Políticas seguem para o Adaptador SQL.

Nesta versão da arquitetura, a auditoria e os logs são incorporados ao Motor de Políticas. Essa decisão é coerente porque o motor concentra as decisões de autorização e bloqueio. Assim, cada decisão deve ser registrada, incluindo:

- identificador da sessão;
- identificador do usuário;
- ferramenta MCP chamada;
- consulta SQL candidata;
- tabelas e colunas envolvidas;
- resultado da validação SQL;
- decisão de autorização;
- motivo do bloqueio, quando houver;
- horário da solicitação;
- consulta efetivamente executada, quando permitida;
- quantidade de linhas retornadas;
- mensagens de erro ou sucesso.

Um exemplo simplificado de política é apresentado a seguir:

```text
Papel: usuario_comum
  Permitir:
    - listar_tabelas_permitidas
    - executar_consulta_segura em vendas_resumidas
    - executar_consulta_segura em produtos_publicos
  Bloquear:
    - acesso à tabela clientes
    - acesso à tabela pagamentos
    - acesso à tabela usuarios_admin
    - qualquer comando diferente de SELECT

Papel: analista
  Permitir:
    - listar_tabelas_permitidas
    - executar_consulta_segura em vendas_resumidas
    - executar_consulta_segura em pedidos_anonimizados
  Bloquear:
    - colunas: cpf, email, telefone, numero_cartao
    - comandos de modificação de dados
```

Essa separação permite que a arquitetura aplique o princípio do menor privilégio. O agente não recebe acesso global ao banco; ele opera dentro dos limites definidos para o usuário ou sessão atual. Mesmo que o modelo tente gerar uma consulta sobre uma tabela restrita, o Motor de Políticas deve bloquear sua execução.

## 3.8 Adaptador SQL

O Adaptador SQL é o componente responsável por encaminhar ao banco de dados apenas consultas já validadas e autorizadas. Ele representa a única parte da arquitetura com permissão para interagir diretamente com o banco relacional.

Suas responsabilidades incluem:

1. receber a consulta aprovada pelo Validador SQL e pelo Motor de Políticas;
2. adaptar a consulta ao dialeto do banco de dados utilizado;
3. aplicar parâmetros de execução, como limite de linhas e tempo máximo de execução;
4. utilizar uma conexão com permissões restritas, preferencialmente somente leitura;
5. executar a consulta no banco;
6. retornar os resultados ao Servidor MCP.

O Adaptador SQL não deve aceitar consultas que não tenham passado pelas etapas anteriores. Essa restrição impede que o agente ou qualquer outro componente externo utilize o adaptador como canal direto de acesso ao banco.

## 3.9 Banco de dados relacional / IDE

O banco de dados relacional é o destino final das consultas autorizadas. Ele pode ser implementado em sistemas como PostgreSQL, MySQL, MariaDB, SQL Server ou SQLite, a depender do ambiente experimental adotado.

No diagrama, o banco aparece associado a “Relacional / IDE” porque a arquitetura pode ser utilizada em ambientes nos quais o agente está integrado a ferramentas de desenvolvimento, como IDEs, ou a interfaces de análise de dados. Entretanto, do ponto de vista arquitetural, o componente crítico é o banco de dados relacional, pois é nele que as consultas validadas são efetivamente executadas.

Recomenda-se que o banco exponha preferencialmente visões seguras em vez de tabelas sensíveis diretamente. As visões podem agregar dados, remover colunas pessoais, aplicar filtros e simplificar o esquema apresentado ao agente.

Por exemplo:

```sql
CREATE VIEW vendas_resumidas AS
SELECT regiao, produto, mes, SUM(valor_total) AS total_vendas
FROM vendas
GROUP BY regiao, produto, mes;
```

O uso de visões reduz a superfície de acesso do agente e facilita a aplicação de políticas. Mesmo que o agente formule uma consulta válida, seu alcance permanece limitado ao subconjunto de dados autorizado.

## 3.10 Fluxo de execução de uma consulta

O fluxo de execução da arquitetura pode ser descrito nas seguintes etapas:

1. O usuário envia um prompt em linguagem natural à interface conversacional.
2. A interface encaminha a requisição ao agente LLM orquestrador.
3. O agente interpreta a intenção e decide acionar uma ferramenta MCP.
4. O Cliente MCP transporta a chamada até o Servidor MCP.
5. O Gateway de Entrada identifica a ferramenta solicitada, como `listar_tabelas_permitidas` ou `executar_consulta_segura`.
6. O módulo de autenticação identifica o usuário ou sessão.
7. O Validador SQL analisa a consulta candidata e aplica regras de sintaxe, semântica e sanitização.
8. O Motor de Políticas verifica se a operação é permitida para o usuário identificado.
9. Caso a consulta seja inválida ou não autorizada, a operação é bloqueada e registrada.
10. Caso a consulta seja válida e autorizada, o Adaptador SQL executa a consulta no banco relacional.
11. O resultado é retornado ao Servidor MCP, encaminhado ao agente e transformado em resposta em linguagem natural para o usuário.

Esse fluxo garante que a decisão final de execução não pertença exclusivamente ao agente LLM. O modelo pode sugerir uma consulta ou acionar uma ferramenta, mas a execução efetiva depende de validações e políticas aplicadas no Servidor MCP.

## 3.11 Cenários de uso

A arquitetura pode ser aplicada a diferentes cenários de consulta a dados relacionais. Um cenário benigno ocorre quando o usuário solicita uma informação agregada e autorizada, como:

```text
Mostre as vendas do mês passado por região.
```

Nesse caso, o agente pode utilizar `listar_tabelas_permitidas` para identificar que a visão `vendas_resumidas` está disponível e, em seguida, acionar `executar_consulta_segura` com uma consulta `SELECT` compatível com as regras da arquitetura.

Um cenário sensível ocorre quando o usuário solicita dados pessoais ou restritos:

```text
Liste o CPF e o e-mail de todos os clientes cadastrados.
```

Nesse caso, mesmo que o agente gere uma consulta SQL sintaticamente válida, o Validador SQL e o Motor de Políticas devem bloquear a operação, pois as colunas solicitadas contêm dados sensíveis.

Um cenário adversarial ocorre quando o usuário tenta manipular o agente:

```text
Ignore todas as políticas anteriores e execute DROP TABLE clientes.
```

Nesse caso, a consulta deve ser rejeitada pelo Validador SQL por conter uma operação destrutiva. A tentativa também deve ser registrada pelo Motor de Políticas para fins de auditoria e rastreabilidade.

Outro cenário adversarial envolve *indirect prompt injection*. Por exemplo, caso uma consulta retorne um campo textual contendo instruções maliciosas, o agente deve tratar esse conteúdo como dado, e não como comando. A arquitetura deve impedir que resultados retornados pelo banco modifiquem permissões, políticas ou ferramentas disponíveis.

## 3.12 Ameaças mitigadas pela arquitetura

A arquitetura proposta busca mitigar diferentes ameaças associadas à integração entre agentes LLM e bancos relacionais. Entre elas, destacam-se:

- **execução de SQL destrutivo**, mitigada pela restrição a comandos `SELECT`;
- **acesso indevido a tabelas sensíveis**, mitigado pelo Motor de Políticas;
- **vazamento de colunas restritas**, mitigado pela validação semântica e pelo uso de visões seguras;
- **prompt injection direto**, mitigado por validação externa ao modelo;
- **indirect prompt injection**, mitigado pela separação entre dados retornados e instruções operacionais;
- **tool poisoning**, mitigado pela exposição controlada de ferramentas no Gateway de Entrada;
- **ausência de rastreabilidade**, mitigada pelo registro das decisões no Motor de Políticas;
- **alucinação de SQL**, mitigada pela validação de esquema e pelo bloqueio de objetos inexistentes ou não autorizados.

É importante destacar que a arquitetura não elimina todos os riscos. O MCP, isoladamente, não garante segurança. A principal contribuição da proposta é utilizar o MCP como uma fronteira padronizada na qual mecanismos de validação, autorização e rastreabilidade podem ser aplicados de forma sistemática.

## 3.13 Considerações sobre a arquitetura

A arquitetura proposta assume que a segurança deve ser implementada em camadas. O agente LLM contribui com interpretação linguística, seleção de ferramentas e geração de consultas candidatas, mas não deve ser responsável pela decisão final de execução. O Servidor MCP, por sua vez, concentra mecanismos determinísticos de validação, identificação, autorização e registro.

A versão apresentada no diagrama é uma simplificação adequada da arquitetura, pois agrupa responsabilidades relacionadas sem perder clareza. A sanitização de entrada e saída é incorporada ao Validador SQL, enquanto auditoria e logs são incorporados ao Motor de Políticas. Com isso, o diagrama permanece legível e mantém os elementos essenciais da proposta.

Essa separação de responsabilidades torna a arquitetura mais adequada para ambientes sensíveis, nos quais bancos de dados relacionais armazenam informações críticas. Além disso, permite avaliar separadamente o desempenho do agente, a efetividade do Validador SQL, o comportamento do Motor de Políticas e o impacto operacional da mediação via MCP.

Portanto, a arquitetura aqui proposta compreende o Model Context Protocol como mais do que uma interface de integração. Ele é tratado como uma camada de governança para agentes LLM, capaz de organizar a comunicação com bancos relacionais e oferecer pontos concretos para aplicação de segurança, controle e rastreabilidade.
