from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from .. import schemas, models, utils
from ..database import get_db
import openai
import os
import json
from dotenv import load_dotenv
from typing import List
import asyncio
import httpx

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

        # Deduzir créditos imediatamente para evitar race conditions
        current_user.credits -= 1
        db.commit()

        prompt = f"""
Você é um assistente educacional com ampla experiência em design instrucional, criação de cursos online e ensino técnico no tema **{course_request.topic}**.

Sua tarefa é gerar um curso completo em **{course_request.language}**, com estrutura progressiva, clareza didática, e conteúdo aprofundado. Use o tom de voz: **{course_request.voice_tone}**.

Geração de Imagem de Capa: {'Sim' if course_request.generate_cover_image else 'Não'}  
Se 'Sim', crie uma descrição coerente com o tema. Caso contrário, ignore essa instrução.

---

## INSTRUÇÕES GERAIS DO CURSO

**Título:** Use [{course_request.topic}], corrigindo erros de escrita, se necessário.  
**Subtítulo:** Crie um subtítulo conciso e cativante, destacando escopo ou benefício do curso.  
**Imagem de capa:** Se aplicável, gere uma descrição coerente e relevante.

---

## ESTRUTURA DO CURSO

- O curso deve conter **3 módulos sequenciais**, com dificuldade crescente.
- Cada módulo deve conter:
  - `"module_title"`: Um nome claro e descritivo
  - `"chapter"`: Uma palavra curta (1 palavra) que represente o módulo (para menu lateral)
  - **6 aulas**, com títulos relevantes e conteúdo técnico crescente
- Cada aula deve ter:
  - `"lesson_title"`: Um título direto e informativo
  - `"content"`: HTML entre **550 e 600 palavras**, estruturado, com ensino progressivo

---

## ORIENTAÇÕES PARA AS AULAS

### 1. Início da Aula
- Comece **diretamente com o conteúdo**.
- **Proibido** o uso de frases introdutórias como: "Nesta aula veremos", "Agora que já estudamos...", ou similares.

### 2. Desenvolvimento
- Apresente o conceito central com profundidade
- Contextualize com aplicações práticas
- Conecte com o que foi aprendido nos módulos anteriores
- Inclua explicações claras, comparações, estudos de caso e dicas
- Evite explicações genéricas ou superficiais

### 3. Estrutura HTML
Use HTML organizado e visualmente agradável:

- `<h2>` ou `<h3>`: para separar seções principais  
- `<strong style="display:block; margin-top:1.5rem; margin-bottom:1.5rem;">`: para subtópicos internos visuais  
- `<ul>` e `<li>`: para listas práticas e estruturadas  
- `<code>` ou `<pre>`: para comandos, trechos técnicos ou sintaxes  
- `<strong>` e `<em>`: para destaques importantes em frases  
- `<p>`: apenas para parágrafos (nunca encapsule tudo em um único `<p>`)  
- `<br>`: para quebras de linha pontuais onde necessário  

### 4. Exemplos e Analogias
- Sempre que possível, inclua **exemplos reais e contextualizados**
- Use analogias para facilitar a compreensão de tópicos mais abstratos

---

## EXERCÍCIOS PRÁTICOS

- Ao final de cada módulo (ou em uma aula estratégica), inclua uma **atividade prática** com **150 a 160 palavras** em HTML
- Tipos de atividade: exercícios, estudo de caso ou quiz rápido
- Sempre que possível, forneça gabarito ou sugestão de resposta comentada

---

## RESUMO FINAL DO CURSO

- Escreva um **resumo com cerca de 150 palavras**, em HTML
- Recapitule os principais pontos e aprendizados

---

## QUESTIONÁRIO FINAL

- Elabore **10 perguntas de múltipla escolha**
- Cada pergunta deve conter **4 alternativas**, com **apenas uma correta**
- Use linguagem clara, objetiva e alinhada com o conteúdo ensinado

---

## FORMATO DE SAÍDA

A resposta deve ser **exclusivamente um JSON** com a estrutura abaixo. Não inclua texto extra:

{{
  "title": "<Título do Curso>",
  "subtitle": "<Subtítulo do Curso>",
  "wallpaper": "<Base64 ou string vazia>",
  "modules": [
    {{
      "module_title": "Título do Módulo",
      "chapter": "NomeDoCapitulo",
      "lessons": [
        {{
          "lesson_title": "Título da Aula",
          "content": "<Conteúdo da aula em HTML, com estrutura progressiva e exemplos práticos>"
        }}
        ...
      ],
      "practice_activities": [
        {{
          "title": "Título da Atividade",
          "content": "<Conteúdo em HTML>"
        }}
      ]
    }}
    ...
  ],
  "final_summary": {{
    "title": "Resumo Final",
    "content": "<Resumo do curso em HTML>"
  }},
  "assessment_quiz": [
    {{
      "text": "Pergunta 1?",
      "alternatives": [
        {{ "text": "Alternativa A", "is_correct": false }},
        {{ "text": "Alternativa B", "is_correct": true }},
        {{ "text": "Alternativa C", "is_correct": false }},
        {{ "text": "Alternativa D", "is_correct": false }}
      ]
    }}
    ...
  ]
}}

---

**IMPORTANTE:**  
- Responda apenas com o JSON acima.  
- Não inclua comentários, explicações ou textos adicionais.  
- Preencha todos os campos com conteúdo real e coerente.  
- O campo `"title"` é obrigatório.
"""


        # Configurar timeout para a chamada da OpenAI
        client = openai.OpenAI()
        
        # Usar timeout para evitar que a operação fique travada
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat.completions.create,
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Você é um especialista em criação de cursos online, com vasta experiência em didática e design instrucional."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                ),
                timeout=300  # 5 minutos de timeout
            )
        except asyncio.TimeoutError:
            # Se timeout, reembolsar o crédito
            current_user.credits += 1
            db.commit()
            raise HTTPException(
                status_code=408,
                detail="Timeout na geração do curso. Tente novamente."
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

            return new_course

        except json.JSONDecodeError as e:
            # Se erro no JSON, reembolsar o crédito
            current_user.credits += 1
            db.commit()
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar resposta da IA: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        # Em caso de erro geral, tentar reembolsar o crédito
        try:
            current_user.credits += 1
            db.commit()
        except:
            pass
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