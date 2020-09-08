# Rossman_challange
Este projeto tem como objetivo simular um desafio real pedido por uma empresa. Para isso utilizei como base os dados da loja Rossmann do desafio [kaggle](https://www.kaggle.com/c/rossmann-store-sales). 
No final foi feito o deploy do modelo no Heroku;

## Contexto
* Reunião mensal de resultados para definição de orçamento;
* CFO pediu uma previsão de vendas das próximas 6 semanas de cada loja;

## Proposta
* Análisar e levar insights sobre as vendas;
* Usar algoritmo de ML capaz de prever as vendas das próximas 6 semanas;
* Fazer deploy do modelo de ML de forma que qualquer pessoa possa acessar as vendas das lojas;

## Pipeline

Os detalhes mais importantes do Pipeline estão no próprio notebook (como gráfico, tabelas e desempenho de modelos).

1. DESCRICAO DOS DADOS
* Preenchimento de NANs
  * Distância de competidores (competition_distance): foi suposto que a competição fica muito distance, logo substituido por 200000;
  * Data de abertura dos competitodes (competition_open_since_month e competition_open_since_year): foi suposto que a competição foi fundada há muito tempo, logo substituido pela data 01/1900;
  * Início da promoção 2 (promo2): foi suposto que a promo 2 terá início em 01/2018 (no futuro);
* Estatística descritiva dos dados numéricos e categóricos;
2. FEATURE ENGINEERING
* Criação de hipóteses por meio de um mapa mental;
* Criação das colunas:
  * is_promo2: 1 se loja participa da promo2 e 0 se não;
  * competition_time_month: tempo que a competição existe em meses
  * promo2_time_week: tempo que há a promo 2 em semanas;
  * assortment: apenas traduz o tipo de assortment
  * state_holiday: faz o mesmo para os feriados
3. FILTRAGEM DE VARIÁVEIS
4. ANALISE EXPLORATORIA DOS DADOS
* Análise univariada, bivariada e multivariada dos dados numéricos e categóricos;
* Alguns insights interessantes foram gerados nessa etapa como (detalhes no notebook):
  * Lojas com COMPETIDORES MAIS PROXIMOS vendem MAIS.
  * Lojas com COMPETIDORES À MAIS TEMPO vendem MENOS.
  * Lojas com promocoes ativas por mais tempo vendem menos, depois de um certo periodo de
  promocao
  * Lojas vendem menos ao longo dos anos
5. DATA PREPARATION
* Etapa de preparação de dados com rescaling e transformação;
* Nesta etapa as instâncias de scale são salvas como pickle para posterior utilização no deploy do modelo;
6. FEATURE SELECTION
* Esta etapa tem como objetivo escolher os melhores features para o treinamento do modelo;
* Para isso é preciso separar os dados de treinamento e teste para cross-validation;
* Foi usado o método Boruta para filtragem das features com maior relevância;
7. MACHINE LEARNING MODELLING
* Utilizando Cross-Validation, foi avaliado qual o melhor método de ML para treinamento do modelo;
* Média de vendas foi utilizado como Baseline;
* Random Forest tem o melhor desempenho, com XGBoost com um desempenho bem próximo;
* Devido ao alto custo computacional de Random Forest, foi escolhido o XGBoost;
8. HYPERPARAMETER FINE TUNING
* Etapa de Fine Tuning do modelo XGBoost, utilizando o método Random Search;
9. TRADUCAO E INTERPRETACAO DO ERRO
* Tradução do erro do modelo em desempenho para o negócio;
* Apresentação de *best case scenario* e *worst case scenario*;
10.0. PASSO 10 - DEPLOY MODEL TO PRODUCTION
* Treinamento do modelo utilizando todo o dado de treinamento. O modelo é salvo como pickle para deploy;
* Construção de uma classe chamada Rossmann para deploy;
* Apesar de não ser o principal objetivo, fiz a submissão no Kaggle com resultado de **0.18594 (RMS)**;
* Deploy do modelo no Heroku;
* Construção e teste da API em Flask no notebook;

## Front End da API

Por último construí uma melhor Front End para a aplicação em flask, dessa forma mesmo quem não é da área técnica poderia acessar a previsão de vendas totais das lojas. Não sou especialista em flask e nem em HTML, o front end é bem minimalista.
Link da API.
