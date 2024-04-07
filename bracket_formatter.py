from __future__ import annotations


class Error:
    MISSING_BRACKET = 'Missing Bracket'


class Wrap:
    def __init__(self, text: str):
        self.text = text.strip()


class A:
    def __init__(self, wrap: Wrap, offset_start: int, offset_end: int, all_inner_a: list, all_inner_b: list):
        self.wrap = wrap
        self.offset_start = offset_start
        self.offset_end = offset_end
        self.all_inner_a = all_inner_a
        self.all_inner_b = all_inner_b or B.parse(self)

    def stringify(self, n_space):
        if self.all_inner_b:
            if len(self.all_inner_b) == 1:
                return '(' + self.all_inner_b[0].stringify(n_space + 1).strip() + ')'
            return '(' + self.all_inner_b[0].stringify(n_space + 1).strip() + ',\n' + ',\n'.join(map(lambda x: x.stringify(n_space + 1), self.all_inner_b[1:])) + ')'
        return '()'

    @staticmethod
    def parse(wrap: Wrap, offset: int = 0) -> A:
        if offset >= len(wrap.text):
            return

        offset_start = wrap.text.find('(', offset)

        if offset_start == -1:
            return

        offset_end = wrap.text.find(')', offset_start + 1)

        if offset_end == -1:
            raise RuntimeError(Error.MISSING_BRACKET)

        all_inner_a = []
        inner_a = A.parse(wrap, offset_start + 1)

        while inner_a is not None and inner_a.offset_start < offset_end:
            offset_end = wrap.text.find(')', inner_a.offset_end + 1)

            if offset_end == -1:
                raise RuntimeError(Error.MISSING_BRACKET)

            all_inner_a.append(inner_a)
            inner_a = A.parse(wrap, inner_a.offset_end + 1)

        return A(wrap, offset_start, offset_end, all_inner_a, None)


class B:
    def __init__(self, a: A, offset_start: int, offset_end: int, inner_a: A):
        self.a = a
        self.offset_start = offset_start
        self.offset_end = offset_end
        self.inner_a = inner_a

    def stringify(self, n_space):
        if self.inner_a is None:
            return ' ' * n_space + self.a.wrap.text[self.offset_start: self.offset_end + 1].strip()
        else:
            text = self.a.wrap.text[self.offset_start: self.inner_a.offset_start].strip()
            return ' ' * n_space + text + self.inner_a.stringify(len(text) + n_space)

    def is_empty(self) -> bool:
        return not bool(self.a.wrap.text[self.offset_start : self.offset_end + 1].strip())

    @staticmethod
    def parse(a: A):
        offset_start = a.offset_start + 1
        offset_end = a.wrap.text.find(',', offset_start)
        all_b = []
        b_a = None
        b_a_ignore = False

        while offset_start < a.offset_end:
            if a.all_inner_a:
                try:
                    inner_a = next(inner_a for inner_a in a.all_inner_a if inner_a.offset_start < offset_end < inner_a.offset_end)
                except StopIteration:
                    inner_a = None

                if inner_a:
                    if b_a is not None:
                        b_a_ignore = True
                        b_a = None

                    elif not b_a_ignore:
                        b_a = inner_a

                    offset_end = a.wrap.text.find(',', inner_a.offset_end + 1)

                    continue

            if offset_end == -1 or offset_end > a.offset_end:
                b = B(a, offset_start, a.offset_end - 1, b_a)

                if not b.is_empty():
                    all_b.append(b)

                break

            b = B(a, offset_start, offset_end - 1, b_a)

            if not b.is_empty():
                all_b.append(b)

            offset_start = offset_end + 1
            offset_end = a.wrap.text.find(',', offset_start)
            b_a = None
            b_a_ignore = False

        return all_b


def format_text(text: str) -> str:
    text = text.replace('\t', ' ' * 4)
    wrap = Wrap(text)
    dummy_a = A(wrap, -1, len(wrap.text), [A.parse(wrap)], None)
    b = dummy_a.all_inner_b[0]
    b_text = wrap.text[b.offset_start: b.inner_a.offset_start]
    n_space = next(len(x) - len(x.lstrip()) for x in text.split('\n') if b_text in x)
    text = b.stringify(n_space)
    return text
