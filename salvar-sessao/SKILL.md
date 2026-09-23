---
name: salvar-sessao
description: Salva o histórico completo da conversa da sessão atual (mensagens do usuário, respostas, chamadas de ferramentas e seus outputs) em um arquivo Markdown (.md). Recebe como argumento o caminho completo do arquivo de destino; se não receber, pergunta ao usuário onde salvar. Use sempre que o usuário pedir para salvar, exportar, registrar, arquivar ou fazer backup da sessão/conversa/histórico/transcript, ou digitar /salvar-sessao, mesmo que não cite o formato .md.
---

# Salvar sessão

Exporta a sessão corrente para um único arquivo `.md`, com tudo o que aconteceu: falas do usuário, respostas do Claude, chamadas de ferramentas e seus resultados.

## Por que usar o script

O Claude Code grava cada sessão em um transcript `.jsonl` em `~/.claude/projects/`. Converter esse arquivo é fiel e completo (outputs de ferramentas longos incluídos). Reescrever a conversa de memória perderia detalhes e gastaria muitos tokens. Por isso, use sempre `scripts/exportar_sessao.py` em vez de redigir o conteúdo manualmente.

## Passos

1. **Descobrir o destino.**
   - Se o usuário passou um argumento, ele é o caminho completo do arquivo (ex.: `~/docs/sessao-x.md`).
   - Se não passou nada, pergunte onde ele quer salvar (caminho completo com nome do arquivo) e aguarde a resposta. Não invente um local. Se estiver em modo que evita perguntas, ainda assim pergunte: sem destino não há como agir.
   - Se o caminho apontar para um diretório existente, peça o nome do arquivo (ou sugira `<diretório>/sessao-AAAA-MM-DD.md` e confirme).

2. **Descobrir o session id.** O path do scratchpad no prompt de sistema termina em `.../<session-id>/scratchpad`; use esse UUID. Ele garante que sessões paralelas no mesmo diretório não se misturem. Se não achar, omita `--session-id` e o script usa o transcript mais recente do diretório atual.

3. **Rodar o script.**

   ```bash
   python3 ~/.claude/skills/salvar-sessao/scripts/exportar_sessao.py "<destino>" --session-id <uuid>
   ```

   - Extensão `.md` é adicionada se faltar; pastas ausentes são criadas; `~` é expandido.
   - Se o script responder `EXISTE: ...`, pergunte ao usuário se pode sobrescrever. Só com confirmação, rode de novo com `--sobrescrever`.

4. **Confirmar.** Diga em uma ou duas frases o caminho salvo e o tamanho. Avise que mensagens trocadas depois do export não entram no arquivo.

## Formato do arquivo

Cabeçalho com metadados (session id, diretório, início/fim, nº de mensagens), depois uma seção `## Usuário`, `## Claude` ou `## Resultado` por mensagem, com timestamp. Chamadas de ferramentas e resultados ficam em blocos `<details>` recolhíveis para o arquivo continuar legível. Blocos de raciocínio interno (thinking) não são exportados, pois o transcript os guarda vazios/criptografados.

## Observações

- O arquivo pode conter dados sensíveis vistos na sessão (conteúdo de arquivos, variáveis de ambiente, tokens em outputs). Se o destino estiver dentro de um repositório git, avise o usuário para não versionar.
- Não faça `git add`/commit do arquivo gerado.
