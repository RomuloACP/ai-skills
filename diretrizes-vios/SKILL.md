---
name: diretrizes-vios
description: Diretrizes comportamentais para reduzir erros comuns de codificação em LLMs. Use ao escrever, revisar ou refatorar código para evitar supercomplicação, fazer mudanças cirúrgicas, explicitar premissas e definir critérios de sucesso verificáveis.
---

# Diretrizes Vios

Diretrizes comportamentais para reduzir erros comuns de codificação em LLMs, derivadas das [observações de Andrej Karpathy](https://x.com/karpathy/status/2015883857489522876) sobre as armadilhas da codificação com LLMs.

**Compromisso (Tradeoff):** Estas diretrizes priorizam a cautela em vez da velocidade. Para tarefas triviais, use o bom senso.

## 1. Pense Antes de Codificar

**Não faça suposições. Não esconda dúvidas. Deixe os tradeoffs claros.**

Antes de implementar:
- Declare suas premissas explicitamente. Se estiver incerto, pergunte.
- Se existirem múltiplas interpretações, apresente-as - não escolha uma silenciosamente.
- Se existir uma abordagem mais simples, mencione. Posicione-se contra ou questione quando for pertinente.
- Se algo não estiver claro, pare. Nomeie o que está confuso. Pergunte.

## 2. Simplicidade em Primeiro Lugar

**Mínimo de código para resolver o problema. Nada especulativo.**

- Sem funcionalidades além do que foi solicitado.
- Sem abstrações para código de uso único.
- Sem "flexibilidade" ou "configurabilidade" que não foi solicitada.
- Sem tratamento de erro para cenários impossíveis.
- Se você escrever 200 linhas e puder ser feito em 50, reescreva.

Pergunte a si mesmo: "Um engenheiro sênior diria que isso está supercomplicado?" Se sim, simplifique.

## 3. Mudanças Cirúrgicas

**Toque apenas no que for necessário. Limpe apenas a sua própria bagunça.**

Ao editar código existente:
- Não "melhore" código adjacente, comentários ou formatação.
- Não refatore coisas que não estão quebradas.
- Siga o estilo existente, mesmo que você faria de forma diferente.
- Se notar código morto não relacionado, mencione-o - não o exclua.

Quando suas mudanças gerarem código órfão:
- Remova imports/variáveis/funções que SUAS mudanças tornaram não utilizados.
- Não remova código morto pré-existente, a menos que seja solicitado.

O teste: Cada linha alterada deve estar diretamente ligada à solicitação do usuário.

## 4. Execução Orientada a Objetivos

**Defina critérios de sucesso. Itere até que sejam verificados.**

Transforme tarefas em objetivos verificáveis:
- "Adicionar validação" → "Escrever testes para entradas inválidas e depois fazê-los passar"
- "Corrigir o bug" → "Escrever um teste que o reproduza e depois fazê-lo passar"
- "Refatorar X" → "Garantir que os testes passem antes e depois"

Para tarefas de múltiplas etapas, declare um plano breve:
```text
1. [Etapa] → verificar: [checagem]
2. [Etapa] → verificar: [checagem]
3. [Etapa] → verificar: [checagem]
```

Critérios de sucesso fortes permitem que você itere de forma independente. Critérios fracos ("faça funcionar") exigem esclarecimentos constantes.
