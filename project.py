import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import re
from datetime import datetime

# ==========================================
# 1. BANCO DE DADOS E LÓGICA DE NEGÓCIO
# ==========================================

def init_db():
    """Inicializa o banco de dados SQLite local."""
    conn = sqlite3.connect("linkary.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_unknown_name():
    """Busca o maior número de 'Unknow' existente e retorna o próximo (ex: Unknow4)."""
    conn = sqlite3.connect("linkary.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM links WHERE name LIKE 'Unknow%'")
    names = cursor.fetchall()
    conn.close()
    
    max_num = 0
    # Expressão regular para capturar apenas "Unknow" seguido de números
    pattern = re.compile(r"^Unknow(\d+)$")
    
    for (name,) in names:
        match = pattern.match(name)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
                
    return f"Unknow{max_num + 1}"

def save_link(name, url, description):
    """Salva o link aplicando as regras de validação, timestamp e nomenclatura."""
    if not url.strip():
        messagebox.showwarning("Aviso", "Insira um link URL")
        return False
        
    # Regra do nome vazio
    if not name.strip():
        name = generate_unknown_name()

    # Verificando se o nome inserido já existe no banco
    conn = sqlite3.connect("linkary.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM links WHERE name = ?", (name,))
    resultado = cursor.fetchone() # Traz o primeiro nome igual que encontrar, se houver
    conn.close()

    if resultado is not None:
        messagebox.showwarning("Aviso", "Esse nome já existe. Digite um nome diferente")
        return False

    # Formato exato solicitado: aaaa-mm-dd/hh:mm:ss
    timestamp = datetime.now().strftime("%Y-%m-%d/%H:%M:%S")
    
    conn = sqlite3.connect("linkary.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO links (name, url, timestamp, description) VALUES (?, ?, ?, ?)",
        (name.strip(), url.strip(), timestamp, description.strip())
    )
    conn.commit()
    conn.close()
    return True

# ==========================================
# 2. INTERFACE GRÁFICA (TKINTER)
# ==========================================

class LinkaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linkary - Sua Livraria de Links")
        self.root.geometry("750x600")
        
        init_db()
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # --- PAINEL DE CADASTRO (TOPO) ---
        register_frame = tk.LabelFrame(self.root, text=" Adicionar Novo Link ", padx=10, pady=10)
        register_frame.pack(fill="x", padx=15, pady=10)
        
        tk.Label(register_frame, text="Nome:").grid(row=0, column=0, sticky="w")
        self.ent_name = tk.Entry(register_frame, width=30)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(register_frame, text="URL:").grid(row=0, column=2, sticky="w")
        self.ent_url = tk.Entry(register_frame, width=40)
        self.ent_url.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(register_frame, text="Descrição:").grid(row=1, column=0, sticky="w")
        self.ent_desc = tk.Entry(register_frame)
        self.ent_desc.grid(row=1, column=1, columnspan=3, sticky="we", padx=5, pady=5)
        
        btn_save = tk.Button(register_frame, text="Salvar Link", bg="#4CAF50", fg="white", command=self.handle_save)
        btn_save.grid(row=2, column=3, sticky="e", padx=5, pady=5)

        # --- PAINEL DE FILTROS E BUSCA (MEIO) ---
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(fill="x", padx=15, pady=5)
        
        tk.Label(filter_frame, text="Buscar:").pack(side="left")
        self.ent_search = tk.Entry(filter_frame, width=30)
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<KeyRelease>", lambda event: self.load_data()) # Busca em tempo real
        
        # Ordenação
        tk.Label(filter_frame, text="Ordenar por:").pack(side="left", padx=(15, 5))
        self.sort_var = tk.StringVar(value="Data")
        rb_date = tk.Radiobutton(filter_frame, text="Data", variable=self.sort_var, value="Data", command=self.load_data)
        rb_name = tk.Radiobutton(filter_frame, text="Nome", variable=self.sort_var, value="Nome", command=self.load_data)
        rb_link = tk.Radiobutton(filter_frame, text="Link", variable=self.sort_var, value="Link", command=self.load_data)
        
        rb_date.pack(side="left")
        rb_name.pack(side="left")
        rb_link.pack(side="left")

        # Deletar
        self.btn_delete = tk.Button(
            filter_frame, 
            text="Deletar", 
            bg="#f44336", 
            fg="white", 
            command=self.handle_delete
        )
        self.btn_delete.pack(side="right", padx=5)

        # Botão Copiar (Pode ser verde claro ou azul para diferenciar do Deletar)
        self.btn_copy = tk.Button(
            filter_frame, 
            text="Copiar Link", 
            bg="#2196F3", # Azul bonito
            fg="white", 
            command=self.handle_copy # Chama a função que vai fazer a cópia
        )
        self.btn_copy.pack(side="right", padx=5)

        # Editar
        self.btn_edit = tk.Button(
            filter_frame, 
            text="Editar", 
            bg="#FF9800", # Escolha a sua cor aqui!
            fg="white", 
            command=self.handle_edit
        )
        self.btn_edit.pack(side="right", padx=5)

        # --- LISTAGEM DE LINKS (INFERIOR - DIRETO AO PONTO) ---
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Configuração da Tabela (Treeview)
        columns = ("name", "url", "timestamp", "description")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.tree.heading("name", text="Nome")
        self.tree.heading("url", text="URL (Link)")
        self.tree.heading("timestamp", text="Data/Hora")
        self.tree.heading("description", text="Descrição")
        
        self.tree.column("name", width=120)
        self.tree.column("url", width=200)
        self.tree.column("timestamp", width=140)
        self.tree.column("description", width=200)
        
        # Barra de rolagem para a tabela
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def handle_save(self):
        name = self.ent_name.get()
        url = self.ent_url.get()
        desc = self.ent_desc.get()
        
        if save_link(name, url, desc):
            # Limpa os campos após salvar
            self.ent_name.delete(0, tk.END)
            self.ent_url.delete(0, tk.END)
            self.ent_desc.delete(0, tk.END)
            self.load_data() # Atualiza a tela imediatamente

    def load_data(self):
        """Busca, filtra, ordena os dados no banco e atualiza a tabela na tela."""
        # Limpa o que já está na tabela antes de recarregar
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search_query = self.ent_search.get().strip()
        sort_option = self.sort_var.get()
        
        # Mapeamento da ordenação para colunas do SQL
        order_column = "timestamp DESC" # Padrão: mais recentes primeiro
        if sort_option == "Nome":
            order_column = "name COLLATE NOCASE ASC" # Ignora maiúsculas/minúsculas
        elif sort_option == "Link":
            order_column = "url ASC"
            
        conn = sqlite3.connect("linkary.db")
        cursor = conn.cursor()
        
        # Query que busca pelo Nome, Link ou Timestamp ao mesmo tempo
        sql = f"""
            SELECT name, url, timestamp, description 
            FROM links 
            WHERE name LIKE ? OR url LIKE ? OR timestamp LIKE ?
            ORDER BY {order_column}
        """
        param = f"%{search_query}%"
        cursor.execute(sql, (param, param, param))
        rows = cursor.fetchall()
        conn.close()
        
        # Insere os dados filtrados na tabela da tela
        for row in rows:
            self.tree.insert("", tk.END, values=row)
    
    def handle_copy(self):
        """Copia a URL do registro selecionado para a área de transferência."""
        # 1. Pega o item selecionado
        selected_items = self.tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione um registro para copiar o link")
            return
            
        # 2. Pega a primeira linha selecionada (caso ele selecione várias, pegamos a primeira)
        item = selected_items[0]
        valores = self.tree.item(item, "values")
        
        # O Nome está em valores[0], a URL está em valores[1]
        url_do_link = valores[1]
        
        # 3. O SEGREDO DO PYTHON: Limpa e copia para a memória do computador
        self.root.clipboard_clear()
        self.root.clipboard_append(url_do_link)
        
        # 4. Feedback para o usuário saber que deu certo
        messagebox.showinfo("Copiado", "Link copiado para a área de transferência!")

    def handle_edit(self):
        """Pega o link selecionado, joga de volta para os campos de entrada e remove o antigo."""
        # 1. Pega os itens selecionados na tabela
        selected_items = self.tree.selection()
        
        # Validação: Se não selecionou nada, avisa o usuário e para
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione um registro para editar")
            return
            
        # 2. Pegamos a linha selecionada e extraímos os valores atuais
        item = selected_items[0]
        valores = self.tree.item(item, "values")
        
        nome_atual = valores[0]
        url_atual = valores[1]
        desc_atual = valores[2] if len(valores) > 3 else valores[3] # Garante pegar a descrição
        
        # 3. O PULO DO GATO: Limpa os campos de cima e joga os dados antigos lá dentro
        self.ent_name.delete(0, tk.END)
        self.ent_name.insert(0, nome_atual)
        
        self.ent_url.delete(0, tk.END)
        self.ent_url.insert(0, url_atual)
        
        self.ent_desc.delete(0, tk.END)
        self.ent_desc.insert(0, valores[3]) # Coluna da descrição
        
        # 4. Remove o registro antigo do banco de dados para não ficar duplicado
        conn = sqlite3.connect("linkary.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM links WHERE name = ?", (nome_atual,))
        conn.commit()
        conn.close()
        
        # Atualiza a tabela tirando o link dali (já que ele subiu para os campos de texto)
        self.load_data()
        
        # Avisa o usuário o que ele deve fazer agora
        messagebox.showinfo("Modo Edição", "Os dados foram enviados para o topo. Modifique e clique em 'Salvar Link'!")


    def handle_delete(self):
        """Gerencia a exclusão de um ou múltiplos registros selecionados."""
        # 1. Pega os itens selecionados na tabela (retorna uma lista de identificadores internos)
        selected_items = self.tree.selection()
    
        # REGRA 1: Se não selecionou nada, avisa o usuário e aborta
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione o registro a deletar")
            return

        # REGRA 2: Pergunta se confirma a exclusão permanente
        confirmar = messagebox.askyesno("Confirmação", "Excluir permanentemente?")
    
        if confirmar:
            linhas_deletadas = 0
            
            # Abrimos uma conexão única com o banco para realizar todas as exclusões
            conn = sqlite3.connect("linkary.db")
            cursor = conn.cursor()
            
            # Laço para passar de linha em linha nas linhas selecionadas pelo usuário
            for item in selected_items:
                # Recupera a tupla de valores daquela linha específica da tabela
                valores = self.tree.item(item, "values")
                nome_do_link = valores[0]  # O nome guardado na primeira coluna
                
                # Executa o comando de exclusão baseado no nome único do link
                cursor.execute("DELETE FROM links WHERE name = ?", (nome_do_link,))
                
                # Soma 1 ao nosso contador para sabermos quantos foram deletados no total
                linhas_deletadas += 1
                
            # Confirma todas as alterações de uma vez no banco e fecha a conexão
            conn.commit()
            conn.close()
            
            # REGRA 3: Mensagem dinâmica informando a quantidade exata de itens excluídos
            messagebox.showinfo("Sucesso", f"{linhas_deletadas} registro(s) deletado(s) com sucesso!")
            
            # Atualiza imediatamente a interface gráfica para refletir a exclusão
            self.load_data()

# Execução do programa
if __name__ == "__main__":
    root = tk.Tk()
    app = LinkaryApp(root)
    root.mainloop()