class KnowledgeBase:
    """A declarative Knowledge Base storing facts and rules (Horn Clauses)."""
    
    def __init__(self):
        self.facts = set()
        self.rules = []
        
    def tell_fact(self, fact_string: str):
        self.facts.add(fact_string)
        
    def tell_rule(self, premise_list: list, conclusion_string: str):
        self.rules.append((premise_list, conclusion_string))
        
    def clear_facts(self):
        self.facts.clear()

    def forward_chain(self):
        """
        Executes data-driven forward chaining to deduce new facts
        until no more new facts can be inferred.
        """
        new_facts_added = True
        
        while new_facts_added:
            new_facts_added = False
            
            for premises, conclusion in self.rules:
                if conclusion not in self.facts:
                    # Modus Ponens Check
                    if all(premise in self.facts for premise in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True
