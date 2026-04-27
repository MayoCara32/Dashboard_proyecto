from src.config import PROMPT_FORMAT_OPTIONS, PROMPT_STYLE_OPTIONS


def get_prompt_style_options() -> tuple[str, ...]:
    return PROMPT_STYLE_OPTIONS


def get_prompt_format_options() -> tuple[str, ...]:
    return PROMPT_FORMAT_OPTIONS


def get_style_instruction(style: str) -> str:
    style_map = {
        "Ejecutivo": "Redacta una respuesta clara, profesional y orientada a toma de decisiones.",
        "Analítico": "Redacta una respuesta más interpretativa, explicando relaciones y posibles implicaciones.",
        "Breve": "Responde de forma corta, directa y con el mínimo texto suficiente.",
        "Hallazgos clave": "Responde destacando los hallazgos más relevantes en orden de importancia.",
    }
    return style_map.get(style, style_map["Ejecutivo"])


def get_format_instruction(output_format: str) -> str:
    format_map = {
        "Párrafo": "Entrega la respuesta en uno o dos párrafos claros.",
        "Viñetas": "Entrega la respuesta en formato de viñetas.",
        "Tabla markdown": "Si es razonable, entrega una tabla markdown breve; si no lo es, explica por qué y responde en viñetas.",
    }
    return format_map.get(output_format, format_map["Párrafo"])


def build_example_block(output_format: str) -> str:
    if output_format == "Viñetas":
        return """
EJEMPLO DE ESTILO ESPERADO
Pregunta: ¿Qué destaca del análisis actual?
Respuesta esperada:
- La categoría principal es Tecnología.
- La región con mayor utilidad es Norte.
- El contexto actual no permite afirmar nada sobre inventario.
""".strip()

    if output_format == "Tabla markdown":
        return """
EJEMPLO DE ESTILO ESPERADO
Pregunta: ¿Qué hallazgos principales observas?
Respuesta esperada:

| Aspecto | Observación |
|---|---|
| Categoría líder | Tecnología |
| Región destacada | Norte |
| Límite del contexto | No hay evidencia sobre inventario |
""".strip()

    return """
EJEMPLO DE ESTILO ESPERADO
Pregunta: ¿Qué destaca del análisis actual?
Respuesta esperada:
La categoría principal es Tecnología y la región con mayor utilidad es Norte. El contexto actual no permite concluir nada sobre inventario o devoluciones.
""".strip()


def get_prompting_principles() -> list[str]:
    return [
        "Ser específico con la tarea.",
        "Indicar claramente el formato de salida.",
        "Restringir la respuesta al contexto disponible.",
        "Pedir que indique cuando falte información.",
        "Usar ejemplos cuando ayudan a fijar el patrón esperado.",
    ]


def get_model_limitations() -> list[str]:
    return [
        "El modelo no ve automáticamente el DataFrame ni las gráficas; solo recibe el contexto textual que le enviamos.",
        "Si el contexto resumido omite algo, el modelo no puede recuperarlo por sí solo.",
        "Puede producir respuestas plausibles aunque falte evidencia suficiente.",
        "Puede interpretar distinto una pregunta ambigua.",
        "No debe responder con datos externos o recientes si no están en el contexto del dashboard.",
    ]


def build_dashboard_prompt(
    question: str,
    dashboard_context: str,
    style: str,
    output_format: str,
    strict_context: bool = True,
    include_example: bool = False,
) -> str:
    style_instruction = get_style_instruction(style)
    format_instruction = get_format_instruction(output_format)

    strict_rule = (
        "Usa exclusivamente la información del contexto. Si la pregunta requiere algo que no esté en el contexto, dilo explícitamente."
        if strict_context
        else "Prioriza el contexto. Si algo no puede confirmarse, aclara el nivel de incertidumbre."
    )

    example_block = build_example_block(output_format) if include_example else ""

    prompt = f"""
CONTEXTO DEL DASHBOARD
{dashboard_context}

INSTRUCCIONES
- Eres un analista de datos que responde en español.
- {style_instruction}
- {format_instruction}
- {strict_rule}
- Sigue este proceso interno:
  1. Identifica los hechos relevantes del contexto.
  2. Verifica si la pregunta puede responderse con ese contexto.
  3. Redacta la respuesta final sin mostrar estos pasos.
- No inventes cifras, regiones, categorías, clientes ni conclusiones no respaldadas.
- Si la pregunta es demasiado amplia para el contexto disponible, dilo claramente.

{example_block}

PREGUNTA DEL USUARIO
Basado en la información anterior, responde a la siguiente pregunta:
{question}
""".strip()

    return prompt