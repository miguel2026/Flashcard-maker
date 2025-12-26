# Flashcard-maker
Pequeno projeto utilizando Ollama, langgraph, streamlit e supabase para criação de flashcards para o anki.
# Importante:
Troque o src/.streamlit/secrets_example.toml para com valores corretos. Para criar a autenticação do google recomendo este [video](https://youtu.be/QziGFxHM1pA?si=i1vgrJiDLCsyyQHZ). Pode utilizar outra base de dados se quiser.
# Features:

## Tutor:
Pesquisa por meio de LLMs de forma a explicar como um tutor pessoal. OBS: ele ainda não tem acesso a internet e alucina ao dar nome aos chats

### TODO:
- [ ] Adicionar pesquisa a internet
- [ ] Consertar a alucinação na escrita dos tópicos. (provelmente finetunning ou RL)
- [ ] Adicionar conectividade com Obsidian e Notion. (RAG simples)
## Exercises:
Criação de listas de exercicios a partir de um tópico, podendo especificar dificuldade e quantidade de questões.

### TODO:
- [ ] Criar feature
- [ ] Adicionar conectividade com Obsidian e Notion. (RAG simples)

## Flashcards (em construção):
Criação de flashcards salvos no banco de dados que podem ser baixados para o anki.

### TODO:
- [ ] Criar feature
