import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from uuid import uuid4
from enum import Enum
import threading
import time
import os

# Tenta importar Pillow
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Aviso: Biblioteca 'Pillow' não instalada.")

# ==============================================================================
# CAMADA DE DOMÍNIO E SERVIÇO (Regras de Negócio Estritas)
# ==============================================================================

class CategoriaResiduo(str, Enum):
    AZUL = "Azul (Papel/Papelão)"
    VERMELHO = "Vermelho (Plástico)"
    VERDE = "Verde (Vidro)"
    AMARELO = "Amarelo (Metal)"
    LARANJA = "Laranja (Perigosos)"
    MARROM = "Marrom (Orgânico)"
    CINZA = "Cinza (Rejeito/Não Reciclável)"

class UserProfile:
    def __init__(self, nome):
        self.id = str(uuid4())
        self.nome = nome
        self.pontos = 0
        self.nivel = 1

class EcoRecycleService:
    def __init__(self):
        self.users = {}
        self.atividades = []
    
    def criar_usuario(self, nome):
        user = UserProfile(nome)
        self.users[user.id] = user
        return user

    def _analisar_regras_estritas(self, texto_lower):
        """
        Simula o 'cérebro' da Opik AI aplicando as regras de negócio fornecidas.
        Retorna: (Categoria, Instrução, Chain of Thought)
        """
        
        # --- 1. Regra: PERIGOSOS / ESPECIAIS (Prioridade Alta) ---
        termos_laranja = ["pilha", "bateria", "quimico", "tinta", "remedio", "lâmpada", "lampada"]
        if any(t in texto_lower for t in termos_laranja):
            # Exceção específica: Lâmpadas geralmente não são laranja, mas requerem descarte especial
            instrucao = "NÃO descarte no lixo comum. Leve a um posto de coleta específico ou loja de eletrônicos."
            return CategoriaResiduo.LARANJA, instrucao, "Detectado componente químico ou perigoso nocivo ao meio ambiente."

        # --- 2. Regra: REJEITOS / NÃO RECICLÁVEIS (Exceções Comuns) ---
        # Papel sujo/gorduroso, papel higiênico, espelhos, cerâmica, metalizados
        if "pizza" in texto_lower or "gordura" in texto_lower or "sujo" in texto_lower:
            return CategoriaResiduo.CINZA, "Papel engordurado não pode ser reciclado. Lixo comum.", "Identificado material orgânico contaminando o papel."
        
        if "papel higienico" in texto_lower or "guardanapo" in texto_lower or "fralda" in texto_lower or "fita adesiva" in texto_lower:
            return CategoriaResiduo.CINZA, "Lixo sanitário ou contaminado. Descarte no lixo comum.", "Material classificado como rejeito sanitário."
        
        if "salgadinho" in texto_lower or "metalizado" in texto_lower:
            return CategoriaResiduo.CINZA, "Embalagens metalizadas (BOPP) são de difícil reciclagem. Lixo comum.", "Plástico misturado com alumínio identificado."

        if "espelho" in texto_lower or "ceramica" in texto_lower or "porcelana" in texto_lower or "cristal" in texto_lower or "vidro temperado" in texto_lower:
            return CategoriaResiduo.CINZA, "Este tipo de vidro/cerâmica tem ponto de fusão diferente. Lixo comum (embrulhe bem).", "Vidro técnico/cerâmica não compatível com reciclagem comum."
        
        if "esponja de aço" in texto_lower or "clipe" in texto_lower:
            return CategoriaResiduo.CINZA, "Material de difícil triagem ou contaminado.", "Metal muito pequeno ou oxidado."

        # --- 3. Regra: ORGÂNICO ---
        termos_marrom = ["casca", "fruta", "comida", "resto", "folha", "alimento", "cafe", "cha"]
        if any(t in texto_lower for t in termos_marrom):
            return CategoriaResiduo.MARROM, "Ideal para compostagem. Se não tiver, lixo orgânico.", "Matéria orgânica detectada."

        # --- 4. Regra: PLÁSTICO (Vermelho) ---
        termos_vermelho = ["garrafa", "pet", "sacola", "pote", "brinquedo", "isopor", "plastico", "plástico"]
        if any(t in texto_lower for t in termos_vermelho):
            instrucao = "Lave para remover restos de comida. Isopor também vai aqui!"
            return CategoriaResiduo.VERMELHO, instrucao, "Polímeros identificados. Compatível com a lixeira vermelha."

        # --- 5. Regra: PAPEL (Azul) ---
        termos_azul = ["jornal", "revista", "caixa", "papel", "escritorio", "folha", "tetra pak", "longa vida"]
        if any(t in texto_lower for t in termos_azul):
            instrucao = "Não amasse demais e evite molhar. Caixas devem ser desmontadas."
            return CategoriaResiduo.AZUL, instrucao, "Fibra de celulose limpa detectada. Compatível com a lixeira azul."

        # --- 6. Regra: VIDRO (Verde) ---
        if "vidro" in texto_lower or "frasco" in texto_lower:
            instrucao = "Retire a tampa. Se estiver quebrado, embrulhe em jornal ou coloque em caixa de papelão."
            obs = "Vidro embalagem detectado."
            if "quebrado" in texto_lower:
                instrucao = "⚠️ PERIGO: Embrulhe em jornal grosso e coloque em caixa de papelão identificada."
                obs += " Estado físico: Quebrado."
            return CategoriaResiduo.VERDE, instrucao, obs

        # --- 7. Regra: METAL (Amarelo) ---
        termos_amarelo = ["lata", "aluminio", "aco", "metal", "tampinha", "prego", "parafuso"]
        if any(t in texto_lower for t in termos_amarelo):
            return CategoriaResiduo.AMARELO, "Lave para remover resíduos orgânicos. Amasse latas se possível.", "Material ferroso ou alumínio identificado."

        # --- Fallback (Não identificado) ---
        return CategoriaResiduo.CINZA, "Material não identificado com clareza. Na dúvida, descarte no lixo comum.", "Confiança da análise abaixo do limiar aceitável."

    def processar_reciclagem(self, user_id, image_path, texto_usuario):
        user = self.users.get(user_id)
        if not user: return None
        
        # Simula tempo de processamento da IA
        time.sleep(1.0)
        
        # Une o texto da imagem (nome do arquivo) com o texto digitado pelo usuário
        nome_arquivo = os.path.basename(image_path) if image_path else ""
        texto_combinado = f"{nome_arquivo} {texto_usuario}".lower()
        
        # Aplica a lógica de IA simulada
        categoria, instrucao, cot = self._analisar_regras_estritas(texto_combinado)
        
        # Sistema de Pontuação Dinâmico
        pontos_ganhos = 10
        if categoria == CategoriaResiduo.LARANJA:
            pontos_ganhos = 50 # Bônus por descarte perigoso correto
        elif categoria == CategoriaResiduo.CINZA:
            pontos_ganhos = 5  # Pontuação baixa para rejeito
        
        # Atualiza Usuário
        user.pontos += pontos_ganhos
        user.nivel = (user.pontos // 100) + 1
        
        registro = {
            "hora": datetime.now().strftime("%H:%M:%S"),
            "item": texto_usuario if texto_usuario else nome_arquivo,
            "categoria": categoria.value,
            "pontos": pontos_ganhos
        }
        self.atividades.append(registro)
        
        return {
            "item": registro["item"],
            "categoria": categoria,
            "instrucao": instrucao,
            "cot": cot
        }, user, pontos_ganhos

# ==============================================================================
# CAMADA DE APRESENTAÇÃO (Frontend - Mantido igual, apenas ajustado para novas cores)
# ==============================================================================

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.service = EcoRecycleService()
        self.current_user = self.service.criar_usuario("Usuário Demo")
        self.caminho_imagem_selecionada = None 
        
        self.title("Coding Life Environmental - Classificador AI")
        self.geometry("1000x720")
        self.configure(bg="#f0f2f5")
        
        self._montar_layout()
        
    def _montar_layout(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#1a1a1a")

        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(pady=20, fill="x", padx=20)
        
        branding_frame = tk.Frame(header_frame, bg="#f0f2f5")
        branding_frame.pack(side="left")

        if os.path.exists("CODING LIFE LOGO SEM FUNDO.jpg") and HAS_PIL:
            self.logo_image = self._carregar_imagem_safe("CODING LIFE LOGO SEM FUNDO.jpg", (80, 80))
            if self.logo_image:
                tk.Label(branding_frame, image=self.logo_image, bg="#f0f2f5").pack(side="left", padx=(0, 15))
        
        ttk.Label(branding_frame, text="Coding Life\nEnvironmental AI", style="Header.TLabel").pack(side="left")
        self.lbl_stats = ttk.Label(header_frame, text=self._get_user_stats_text(), font=("Consolas", 10, "bold"))
        self.lbl_stats.pack(side="right", anchor="n", pady=10)

        # Main Area
        main_container = tk.Frame(self, bg="#f0f2f5")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Left: Inputs
        left_frame = tk.Frame(main_container, bg="white", bd=1, relief="solid")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="📸 Analisador de Resíduos", bg="white", font=("Helvetica", 12, "bold"), fg="#333").pack(pady=10)

        # Preview
        self.frame_preview = tk.Frame(left_frame, bg="#f8f9fa", width=300, height=180, bd=1, relief="sunken")
        self.frame_preview.pack(pady=5)
        self.frame_preview.pack_propagate(False)
        self.lbl_preview = tk.Label(self.frame_preview, text="Sem imagem", bg="#f8f9fa", fg="#888")
        self.lbl_preview.pack(expand=True, fill="both")

        btn_upload = tk.Button(left_frame, text="📂 Carregar Imagem", bg="#1976d2", fg="white", 
                               font=("Helvetica", 10, "bold"), command=self.acao_selecionar_imagem, cursor="hand2")
        btn_upload.pack(pady=5, fill="x", padx=50)

        tk.Label(left_frame, text="Complemente a descrição (Ex: 'caixa de pizza suja'):", bg="white", fg="#666").pack(pady=(10, 0))
        self.txt_input = tk.Text(left_frame, height=3, font=("Helvetica", 10), bg="#fafafa", relief="solid", bd=1)
        self.txt_input.pack(pady=5, padx=20)

        self.btn_enviar = tk.Button(left_frame, text="PROCESSAR COM IA", bg="#000000", fg="white", 
                                    font=("Helvetica", 11, "bold"), height=2, command=self.acao_reciclar, cursor="hand2")
        self.btn_enviar.pack(pady=15, fill="x", padx=30)
        
        self.lbl_resultado = tk.Label(left_frame, text="Aguardando...", bg="#f5f5f5", fg="#666",
                                      font=("Helvetica", 10), justify="left", relief="flat", padx=10, pady=10)
        self.lbl_resultado.pack(fill="both", expand=True, padx=15, pady=15)

        # Right: Dashboard
        right_frame = tk.Frame(main_container, bg="white", bd=1, relief="solid")
        right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(right_frame, text="📊 Histórico de Triagem", bg="white", font=("Helvetica", 12, "bold"), fg="#333").pack(pady=15)
        
        columns = ("Hora", "Item", "Categ", "Pts")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Item", text="Item")
        self.tree.heading("Categ", text="Categoria")
        self.tree.heading("Pts", text="Pts")
        
        self.tree.column("Hora", width=60, anchor="center")
        self.tree.column("Item", width=120)
        self.tree.column("Categ", width=110)
        self.tree.column("Pts", width=40, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def _carregar_imagem_safe(self, caminho, tamanho):
        if not HAS_PIL: return None
        try:
            img = Image.open(caminho)
            img.thumbnail(tamanho, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception: return None

    def _get_user_stats_text(self):
        return f"👤 {self.current_user.nome} | ⭐ Nível {self.current_user.nivel} | 🏆 {self.current_user.pontos} pts"

    def acao_selecionar_imagem(self):
        arquivo = filedialog.askopenfilename(title="Selecione imagem", filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if arquivo:
            self.caminho_imagem_selecionada = arquivo
            img_preview = self._carregar_imagem_safe(arquivo, (280, 160))
            if img_preview:
                self.lbl_preview.configure(image=img_preview, text="")
                self.lbl_preview.image = img_preview

    def acao_reciclar(self):
        texto = self.txt_input.get("1.0", tk.END).strip()
        if not self.caminho_imagem_selecionada and len(texto) < 3:
            messagebox.showwarning("Dados insuficientes", "Carregue uma imagem ou descreva o item.")
            return

        self.btn_enviar.config(text="Analisando Regras...", state="disabled", bg="#333")
        self.lbl_resultado.config(text="🤖 Aplicando matriz de decisão...", bg="#fff3e0", fg="#e65100")
        threading.Thread(target=self._processar_thread, args=(self.caminho_imagem_selecionada, texto)).start()

    def _processar_thread(self, img_path, texto):
        resultado, user, pontos = self.service.processar_reciclagem(self.current_user.id, img_path, texto)
        self.after(0, self._atualizar_gui, resultado)

    def _atualizar_gui(self, res):
        # Definição de Cores Baseada na Categoria
        cor_map = {
            CategoriaResiduo.AZUL: ("#e3f2fd", "#0d47a1"), # Azul claro / Escuro
            CategoriaResiduo.VERMELHO: ("#ffebee", "#b71c1c"), # Vermelho claro / Escuro
            CategoriaResiduo.VERDE: ("#e8f5e9", "#1b5e20"), # Verde
            CategoriaResiduo.AMARELO: ("#fffde7", "#f57f17"), # Amarelo
            CategoriaResiduo.LARANJA: ("#fff3e0", "#e65100"), # Laranja
            CategoriaResiduo.MARROM: ("#efebe9", "#4e342e"), # Marrom
            CategoriaResiduo.CINZA: ("#f5f5f5", "#616161"), # Cinza
        }
        bg, fg = cor_map.get(res['categoria'], ("#fff", "#000"))

        texto_final = (
            f"✅ RESULTADO: {res['categoria'].value}\n"
            f"──────────────────────────────────\n"
            f"🧠 Raciocínio IA: {res['cot']}\n"
            f"📋 Instrução Técnica: {res['instrucao']}\n"
            f"──────────────────────────────────\n"
            f"🎉 Pontuação computada."
        )
        
        self.lbl_resultado.config(text=texto_final, bg=bg, fg=fg)
        
        # Atualiza Tabela
        # Simplifica o nome da categoria para a tabela não ficar gigante
        cat_short = res['categoria'].value.split("(")[0].strip() 
        ultimo = self.service.atividades[-1]
        self.tree.insert("", 0, values=(ultimo['hora'], ultimo['item'], cat_short, f"+{ultimo['pontos']}"))
        
        self.lbl_stats.config(text=self._get_user_stats_text())
        self.btn_enviar.config(text="PROCESSAR NOVO", state="normal", bg="#000000")
        self.txt_input.delete("1.0", tk.END)
        self.caminho_imagem_selecionada = None
        self.lbl_preview.configure(image="", text="Sem imagem")

if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()