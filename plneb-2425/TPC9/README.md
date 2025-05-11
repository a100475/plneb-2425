#TPC9

O objetivo deste TPC foi analizar os dois livros do Harry Potter e tokenizar o seu conteudo através do uso de Word2Vec.

De seguida, a informação tokenizada foi utilizada para treinar um modelo de vetores com Word2Vec.

Por fim foi gerado metadata.tsv e tensor.tsv ao implementar o commando ```python -m gensim.scripts.word2vec2tensor -i model_harry.txt -o model_harry``` no terminal, sendo estes ficheiros utilizados para a análise do modelo no site: https://projector.tensorflow.org