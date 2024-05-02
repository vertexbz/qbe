from __future__ import annotations


class Optionable:
    only: dict
    unless: dict

    def available(self, options: dict):
        if len(self.only) == 0 and len(self.unless) == 0:
            return True

        result = True
        for key, state in self.only.items():
            result = result and options.get(key, None) == state

        for key, state in self.unless.items():
            if options.get(key, None) == state:
                result = False
                break

        return result
