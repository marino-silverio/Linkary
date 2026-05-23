# Linkary - Sua Livraria de Links

O **Linkary** é um gerenciador de links local desenvolvido em Python. Ele foi criado para resolver o problema de organizar, buscar e utilizar URLs importantes no dia a dia através de uma interface gráfica simples e direto ao ponto.

##  Funcionalidades

- **Salvamento Inteligente:** Salva links com validação de URL. Se o campo de nome for deixado vazio, o sistema gera automaticamente um nome padrão (ex: `Unknow1`, `Unknow2`) sem repetir.
- **Dicas de Uso:** Aviso ao esquecer de adicionar uma descrição, mas permite o salvamento.
- **Busca em Tempo Real:** Barra de pesquisa que filtra os links por nome, URL ou data enquanto você digita.
- **Ordenação Dinâmica:** Permite ordenar a tabela por Data de registro, Nome do link ou URL.
- **Cópia Rápida (Ctrl+C integrado):** Botão que copia o link selecionado direto para a área de transferência do seu computador.
- **Modo Edição:** Botão que envia os dados do link selecionado de volta para os campos do topo para que você faça alterações rapidamente.
- **Exclusão Múltipla:** Permite selecionar um ou vários links (segurando a tecla Ctrl) para deletá-los permanentemente após uma confirmação de segurança.

##  Tecnologias Utilizadas

- **Python** (Linguagem principal)
- **Tkinter / TTK** (Interface gráfica nativa)
- **SQLite3** (Banco de dados local e leve)
- **Re** (Expressões regulares para nomenclatura inteligente)

##  Como Rodar o Projeto

1. Python 3.12.13 ou mais atual instalado na sua máquina
2. Baixe o arquivo `project.py`
3. Abra o terminal ou prompt de comando na pasta do arquivo e execute:
   python project.py