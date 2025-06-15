from lark import Transformer

from sympy_client.grammar import DefinitionStore

class DefStoreBaseTransformer(Transformer):
    
    def __init__(self, definition_store: DefinitionStore = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.definition_store = definition_store
