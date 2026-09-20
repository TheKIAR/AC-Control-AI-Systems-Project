"""First-Order Predicate Logic kernel: terms, atoms, rules, forward chaining.

Semantics: Horn-style rules with variables, grounded over the known
constants. Negated premises use negation-as-failure under a closed-world
assumption (¬P holds when P cannot be derived from the facts).
"""

from itertools import product


class Variable:
    def __init__(self, name):
        self.name = str(name)

    def __repr__(self):
        return f"?{self.name}"


class Constant:
    def __init__(self, name):
        self.name = str(name)

    def __repr__(self):
        return self.name


class Atom:
    """A (possibly negated) predicate applied to terms.

    Terms may be Variable / Constant / plain strings (treated as constants).
    """

    def __init__(self, predicate, args=(), negated=False):
        self.predicate = str(predicate)
        self.args = tuple(args)
        self.negated = bool(negated)

    def ground(self, binding):
        """Substitute variables using binding {var_name: constant_name}."""
        ground_args = []
        for term in self.args:
            if isinstance(term, Variable) and term.name in binding:
                ground_args.append(binding[term.name])
            elif isinstance(term, (Variable, Constant)):
                ground_args.append(term.name)
            else:
                ground_args.append(str(term))
        return (self.predicate, tuple(ground_args))

    def describe(self):
        sign = "¬" if self.negated else ""
        terms = ", ".join(
            ("?" + t.name) if isinstance(t, Variable) else str(getattr(t, "name", t))
            for t in self.args
        )
        return f"{sign}{self.predicate}({terms})"

    def __repr__(self):
        return self.describe()


class Rule:
    """∀ variables. premises → conclusion."""

    def __init__(self, name, variables, premises, conclusion, description=""):
        self.name = str(name)
        self.variables = [str(v) for v in variables]
        self.premises = list(premises)
        self.conclusion = conclusion
        self.description = str(description)

    def __repr__(self):
        body = " ∧ ".join(p.describe() for p in self.premises)
        return f"{self.name}: ∀{','.join(self.variables)}. {body} → {self.conclusion.describe()}"


class KnowledgeBase:
    def __init__(self, constants=()):
        self.constants = [str(c) for c in constants]
        self.facts = set()  # {(predicate, (arg, ...))}
        self.rules = []

    # -- facts ----------------------------------------------------------
    def tell(self, predicate, *args):
        fact = (str(predicate), tuple(str(a) for a in args))
        self.facts.add(fact)
        return fact

    def ask(self, predicate):
        """Return sorted arg-tuples for all facts with this predicate."""
        predicate = str(predicate)
        return sorted(args for pred, args in self.facts if pred == predicate)

    def holds(self, ground_atom):
        return ground_atom in self.facts

    # -- inference ------------------------------------------------------
    def _bindings(self, variables):
        if not variables:
            yield {}
            return
        for combo in product(self.constants, repeat=len(variables)):
            yield dict(zip(variables, combo))

    def forward_chain(self, max_rounds=50):
        """Fire rules to fixpoint. Returns trace of (rule, binding, conclusion)."""
        trace = []
        for _ in range(max_rounds):
            fired_this_round = False
            for rule in self.rules:
                for binding in self._bindings(rule.variables):
                    if all(
                        (not self.holds(premise.ground(binding)))
                        if premise.negated
                        else self.holds(premise.ground(binding))
                        for premise in rule.premises
                    ):
                        conclusion = rule.conclusion.ground(binding)
                        if conclusion not in self.facts:
                            self.facts.add(conclusion)
                            fired_this_round = True
                            trace.append((rule.name, dict(binding), conclusion))
            if not fired_this_round:
                break
        return trace

    def conclusions(self, predicates):
        """Ground action atoms for the given predicate names, sorted."""
        wanted = {str(p) for p in predicates}
        return sorted(
            f"{pred}({', '.join(args)})"
            for pred, args in self.facts
            if pred in wanted
        )

    def describe_trace(self, trace):
        lines = []
        for name, binding, conclusion in trace:
            binds = ", ".join(f"{var}={val}" for var, val in binding.items())
            pred, args = conclusion
            lines.append(f"{name} {{{binds}}}: → {pred}({', '.join(args)})")
        return lines
