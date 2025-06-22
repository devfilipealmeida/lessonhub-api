from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import schemas, models, utils
from ..database import get_db
import openai
import os
import json
from dotenv import load_dotenv
from typing import List

load_dotenv()

router = APIRouter(tags=['Courses'])

@router.post('/generate-course', response_model=schemas.CourseResponse)
async def generate_course(
    course_request: schemas.CourseRequest,
    current_user: models.User = Depends(utils.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera um curso completo usando a API da OpenAI e salva no banco de dados
    """
    try:
        if current_user.credits < 1:
            raise HTTPException(
                status_code=400,
                detail="Créditos insuficientes para gerar o curso"
            )

        prompt = f"""
Você é um especialista em criação de cursos online, com vasta experiência em didática e design instrucional.

Sua tarefa é gerar um curso completo em {course_request.language}, bem estruturado e didático, com base no tópico fornecido pelo usuário, garantindo clareza, engajamento e profundidade adequada ao tema.

**Entrada do Usuário:** {course_request.topic}

Opções de Personalização:

- **Nível de Profundidade:** {course_request.depth_level} (Padrão: Intermediário)
- **Tom de Voz:** {course_request.voice_tone} (Padrão: Formal)
- **Geração de Imagem de Capa:** {'Sim' if course_request.generate_cover_image else 'Não'} (Padrão: Sim)
- **Descrição da Imagem de Capa (se Geração de Imagem de Capa for 'Sim'):** [Descreva a imagem desejada, e.g., 'Um cérebro estilizado com circuitos de IA']

**Instruções para Geração do Curso:**

- **Título do Curso:** [Entrada do Usuário corrigida se houver erros de escrita].
- **Subtítulo do Curso:** Desenvolva um subtítulo conciso e cativante que complemente o título e destaque um benefício chave ou o escopo do curso.
- **Imagem de Capa:** Se a opção 'Geração de Imagem de Capa' for 'Sim', gere uma imagem de capa relevante e de alta qualidade para o curso. Caso contrário, ignore esta instrução.
- **Estrutura do Curso (Módulos e Aulas):** Divida o curso em 3 módulos lógicos e sequenciais. Cada módulo deve conter um título claro e uma série de 6 aulas.
- Cada módulo deve ter um nome de capítulo criativo e em 1 palavra referente ao conteúdo do módulo para ser usado na opção de menus de uma sidebar.
- Cada aula deve ter um título e subtópicos relevantes. Ao final de cada módulo, insira um parágrafo abrangendo o conteúdo das aulas que o aluno viu.
- **Conteúdo Detalhado das Aulas:** Para cada aula, forneça explicações claras, detalhadas e didáticas em formato HTML.
  Incluir exemplos práticos, analogias e, quando aplicável, estudos de caso e exemplos. O conteúdo deve ser aprofundado o suficiente para o nível de profundidade especificado. Numere as aulas no formato '[NumeroModulo].[NumeroAula]'. Exemplo: no módulo 1 teremos: 1.1 + nome ou tópico da aula.
  Utilize entre 500 e 510 palavras para o conteúdo de cada aula.
  Use apenas as tags HTML básicas: p, strong, em, ul, li, code, pre, h1 a h6, a, img (com src e alt).
- **Exercícios Práticos:** Ao final de cada módulo ou em aulas específicas, inclua atividades práticas para fixação do conteúdo. Podem ser exercícios, estudos de caso para análise ou quizzes rápidos. Forneça o enunciado e, se aplicável, um gabarito ou sugestão de solução. Use entre 150 e 160 palavras. O conteúdo deve ser em HTML.
- **Resumo Final do Curso:** Crie um resumo abrangente em HTML, recapitulando os principais pontos abordados em todo o curso e reforçando os aprendizados. Use 150 palavras.
- **Questionário de Avaliação:** Desenvolva um questionário final com 10 perguntas de múltipla escolha para testar o conhecimento adquirido. Cada pergunta deve ter um enunciado claro e 4 alternativas, sendo apenas uma correta.

**Observações:** A IA deve se esforçar para manter a consistência no tom de voz e no nível de profundidade ao longo de todo o curso. Use apenas as tags HTML permitidas para o conteúdo: p, strong, em, ul, li, code, pre, h1 a h6, a, img (com src e alt).

## Output Format

A saída deve ser estruturada em JSON, seguindo o modelo abaixo:

{{

 "title": "<Título do Curso>",

 "subtitle": "<Subtítulo do Curso>",

 "wallpaper": "<URL ou descrição da imagem de capa>",

 "modules": [

  {{

   "module_title": "Título do Módulo 1",

   "chapter": "NomeDoCapitulo",

   "lessons": [

​    {{

​     "lesson_title": "1.1 Nome da Aula",

​     "content": "<p>Conteúdo da aula em HTML...</p>"

​    }},

​    {{

​     "lesson_title": "1.2 Nome da Aula",

​     "content": "<p>Conteúdo da aula em HTML...</p>"

​    }}

   ],

   "practice_activities": [

​    {{

​     "title": "Título da Atividade",

​     "content": "<p>Descrição da atividade em HTML...</p>"

​    }}

   ]

  }},

  {{

   "module_title": "Título do Módulo 2",

   "chapter": "NomeDoCapitulo",

   "lessons": [

​    {{

​     "lesson_title": "2.1 Nome da Aula",

​     "content": "<p>Conteúdo da aula em HTML...</p>"

​    }},

​    {{

​     "lesson_title": "2.2 Nome da Aula",

​     "content": "<p>Conteúdo da aula em HTML...</p>"

​    }}

   ],

   "practice_activities": [

​    {{

​     "title": "Título da Atividade",

​     "content": "<p>Descrição da atividade em HTML...</p>"

​    }}

   ]

  }},

  {{

   "module_title": "Título do Módulo 3",

   "chapter": "NomeDoCapitulo",

   "lessons": [

​    {{

​     "lesson_title": "3.1 Nome da Aula",

​     "content": "<p>Conteúdo da aula em HTML...</p>"

​    }},

​    {{

​     "lesson_title": "3.2 Nome da Aula",

​     "content": "<p>Conteúdo da aula em HTML...</p>"

​    }}

   ],

   "practice_activities": [

​    {{

​     "title": "Título da Atividade",

​     "content": "<p>Descrição da atividade em HTML...</p>"

​    }}

   ]

  }}

 ],

 "final_summary": {{

  "title": "Resumo Final",

  "content": "<p>Resumo final em HTML...</p>"

 }},

 "assessment_quiz": [

  {{

   "text": "Pergunta 1?",

   "alternatives": [

​    {{

​     "text": "Alternativa A",

​     "is_correct": false

​    }},

​    {{

​     "text": "Alternativa B",

​     "is_correct": true

​    }},

​    {{

​     "text": "Alternativa C",

​     "is_correct": false

​    }},

​    {{

​     "text": "Alternativa D",

​     "is_correct": false

​    }}

   ]

  }}

 ]

}}

Para imagens de capa, utilize a base64 em string ou uma string vazia.

Siga rigorosamente este formato para a saída completa do curso.

IMPORTANTE: Responda APENAS com o JSON, sem explicações, comentários ou texto adicional. 
Preencha todos os campos com o conteúdo real do curso gerado, não use textos genéricos ou exemplos. 
O campo 'title' é obrigatório no JSON de saída.
"""

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em criação de cursos online, com vasta experiência em didática e design instrucional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        response_text = response.choices[0].message.content

        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```", 1)[0]
            elif "```" in response_text:
                response_text = response_text.split("```", 1)[1]

            course_data = json.loads(response_text.strip())

            new_course = models.Course(
                title=course_data["title"],
                subtitle=course_data["subtitle"],
                wallpaper=course_data["wallpaper"],
                modules=course_data["modules"],
                final_summary=course_data["final_summary"],
                assessment_quiz=course_data["assessment_quiz"],
                language=course_request.language,
                depth_level=course_request.depth_level,
                voice_tone=course_request.voice_tone,
                user_id=current_user.id
            )

            db.add(new_course)
            db.commit()
            db.refresh(new_course)

            current_user.credits -= 1
            db.commit()

            return new_course

        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar resposta da IA: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar curso: {str(e)}"
        )

@router.get('/my-courses', response_model=List[schemas.CourseList])
def get_my_courses(
    current_user: models.User = Depends(utils.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os cursos do usuário autenticado (apenas id e título)
    """
    courses = db.query(models.Course).filter(models.Course.user_id == current_user.id).all()
    return courses 

@router.get('/courses/{course_id}', response_model=schemas.CourseResponse)
def get_course(
    course_id: int,
    current_user: models.User = Depends(utils.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Busca um curso específico pelo ID (apenas se o usuário for o dono)
    """
    course = db.query(models.Course).filter(
        models.Course.id == course_id,
        models.Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Curso não encontrado ou você não tem permissão para acessá-lo"
        )
    
    return course 