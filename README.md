# 🧠 Projeto 01 – Inteligência Artificial (IA25_P01_G01)

## 🎯 Introdução
O objetivo deste projeto é desenvolver um **agente inteligente** capaz de **gerar horários de aulas automaticamente**, respeitando um conjunto de **restrições rígidas (hard constraints)** e **restrições flexíveis (soft constraints)**.

O projeto é desenvolvido em **Python**, usando **Jupyter Notebook** e a biblioteca [`python-constraint`](https://pypi.org/project/python-constraint/).

---

## 👥 Elementos do Grupo
| Nome | Número de Estudante |
|------|----------------------|
| Joel Faria | 28001 |
| Nuno Silva | 28005 |
| Diogo Graça | 28004 |
| Gonçalo Gomes | 25455 |
| Hugo Monteiro | 27993 |

---

## ⚙️ Ferramentas e Tecnologias
- **Linguagem:** Python  
- **Ambiente:** Jupyter Notebook  
- **Bibliotecas principais:**
  - [`python-constraint`](https://pypi.org/project/python-constraint/)
  - json

---

## 🧩 Formulação do Problema (CSP)
O problema é formulado como um **Constraint Satisfaction Problem (CSP)**, onde:

### 🔸 Variáveis
Representam as aulas, cursos, professores e salas.

### 🔸 Domínios
Possíveis horários disponíveis para cada aula.

### 🔸 Restrições Rígidas (Hard Constraints)
- Cada aula dura **2 horas**  
- Cada curso pode ter **1 ou 2 aulas por semana**  
- Uma turma **não pode ter mais de 3 aulas por dia**  
- O horário deve respeitar a **disponibilidade dos docentes**

---

## 🚀 Execução e Resultados
O notebook deverá:
1. Encontra e mostra ** a primeira solução possível**  


---

## 🧠 Conclusão
O agente desenvolvido deve ser capaz de gerar horários válidos que satisfaçam as restrições impostas, demonstrando o potencial da **Inteligência Artificial baseada em CSPs** na resolução de problemas de otimização complexos.
