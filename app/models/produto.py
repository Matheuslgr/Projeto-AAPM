#Tabela de produtos

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nome  = Column(String(150), nullable=False, index=True)
    preco = Column(Float, nullable=False, default=0.1)
    preco_associado = Column(Float, nullable=True)
    estoque_atual = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, default=True)

    #Imagem
    imagem_path = Column(String(255), nullable=True)

    #Chave estrangeira
    categoria_id = Column(Integer, ForeignKey("categorias.id", onupdate="SET NULL"), nullable=True)

    #Relacionamento

    categoria = relationship("Categoria", back_populates="produtos")

    @property
    def imagem_url(self):
        if self.imagem_path:
            return f"/static/{self.imagem_path}"
        else:
            return "/static/img/produto-placeholder.png"
        
    @property
    def possui_estoque(self):
        return self.estoque_atual <= 10
    