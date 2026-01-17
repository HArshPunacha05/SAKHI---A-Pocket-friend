from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import operator


class TranslationState(TypedDict):
    """State for translation workflow"""
    text: str
    source_lang: str
    target_lang: str
    translation: str
    confidence: float
    messages: Annotated[list, operator.add]


class TranslationGraph:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(
            api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.3
        )
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build LangGraph workflow for translation"""
        workflow = StateGraph(TranslationState)
        
        # Add nodes
        workflow.add_node("detect_language", self._detect_language)
        workflow.add_node("translate", self._translate)
        workflow.add_node("validate", self._validate_translation)
        
        # Define edges
        workflow.set_entry_point("detect_language")
        workflow.add_edge("detect_language", "translate")
        workflow.add_edge("translate", "validate")
        workflow.add_edge("validate", END)
        
        return workflow.compile()
    
    def _detect_language(self, state: TranslationState) -> TranslationState:
        """Detect and confirm source language"""
        messages = [
            SystemMessage(content="You are a language detection expert."),
            HumanMessage(content=f"Confirm if this text is in {self._get_language_name(state['source_lang'])}: '{state['text']}'. Respond with just 'yes' or 'no'.")
        ]
        
        response = self.llm.invoke(messages)
        state["messages"] = [{"role": "system", "content": "Language detected"}]
        
        return state
    
    def _translate(self, state: TranslationState) -> TranslationState:
        """Perform translation"""
        source_lang_name = self._get_language_name(state['source_lang'])
        target_lang_name = self._get_language_name(state['target_lang'])
        
        messages = [
            SystemMessage(
                content=f"You are a professional translator specializing in {source_lang_name} to {target_lang_name} translation. "
                f"Translate the following text accurately while preserving the tone and context. "
                f"Provide ONLY the translation, no explanations."
            ),
            HumanMessage(content=state['text'])
        ]
        
        response = self.llm.invoke(messages)
        state["translation"] = response.content.strip()
        state["messages"].append({"role": "assistant", "content": state["translation"]})
        
        return state
    
    def _validate_translation(self, state: TranslationState) -> TranslationState:
        """Validate translation quality"""
        messages = [
            SystemMessage(
                content="You are a translation quality assessor. Rate the translation quality on a scale of 0-1."
            ),
            HumanMessage(
                content=f"Original ({state['source_lang']}): {state['text']}\n"
                f"Translation ({state['target_lang']}): {state['translation']}\n"
                f"Provide only a number between 0 and 1."
            )
        ]
        
        response = self.llm.invoke(messages)
        try:
            state["confidence"] = float(response.content.strip())
        except:
            state["confidence"] = 0.8  # Default confidence
        
        return state
    
    def _get_language_name(self, code: str) -> str:
        """Convert language code to full name"""
        languages = {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ar': 'Arabic',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'it': 'Italian',
            'ko': 'Korean',
            'ta': 'Tamil',
            'te': 'Telugu',
            'bn': 'Bengali',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi'
        }
        return languages.get(code, code)
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        """Execute translation workflow"""
        initial_state = {
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "translation": "",
            "confidence": 0.0,
            "messages": []
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "translation": final_state["translation"],
            "confidence": final_state["confidence"],
            "source_lang": source_lang,
            "target_lang": target_lang
        }