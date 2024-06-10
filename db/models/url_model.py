from __future__ import annotations
import datetime
from dataclasses import dataclass

# header 요소들의 bit정보
@dataclass
class Bit():
    start:int # 시작 bit -> 0 부터 시작
    lenght:int # bit 길이

    @property
    def sum(self): # 끝나는 bit (포함 x)
        return self.start + self.lenght
    
    @property
    def start_byte(self): # 시작 byte
        return self.start // 8
    
    @property
    def end_byte(self): # 끝나는 byte (포함 o)
        return ((self.sum - 1) // 8)
    
    @property
    def beyt_lenght(self): # byte 길이
        return self.end_byte - self.start_byte + 1
    
    def __repr__(self) -> str:
        return f"bit({self.lenght}) : {self.start} -> {self.sum}\nbyte({self.beyt_lenght}) : {self.start_byte} ~ {self.end_byte}"

VIEW_BIT = Bit(0, 31)
IS_EXP_BIT = Bit(VIEW_BIT.sum, 1)
YEAR_BIT = Bit(IS_EXP_BIT.sum, 12)
MONTH_BIT = Bit(YEAR_BIT.sum, 4)
DAY_BIT = Bit(MONTH_BIT.sum, 6)
HOUR_BIT = Bit(DAY_BIT.sum, 6)
MINUTE_BIT = Bit(HOUR_BIT.sum, 6)
SENCOND_BIT = Bit(MINUTE_BIT.sum, 6)

BITS:list[Bit] = [
    VIEW_BIT, IS_EXP_BIT, YEAR_BIT, MONTH_BIT, DAY_BIT, HOUR_BIT, MINUTE_BIT, SENCOND_BIT
]

# 제곱 연산 가독성 및 시간 복잡도 땜에 미리 만듦
left_bit_gap = [
    0b11111111, 0b01111111, 0b00111111, 0b00011111,
    0b00001111, 0b00000111, 0b00000011, 0b00000001
]
right_bit_gap = [
    0b11111111, 0b11111110, 0b11111100, 0b11111000,
    0b11110000, 0b11100000, 0b11000000, 0b10000000
]

class UrlModel():
    def __init__(self, b: bytes) -> None:
        self.b:bytearray = bytearray(b)

    def get_header(self, bit: Bit): # bytearray에서 Bit로 feild 구하기
        b = self.b[bit.start_byte:bit.end_byte + 1]
        if bit.start_byte > 0:
            l_gap = bit.start % (bit.start_byte * 8)
        else:
            l_gap = bit.start
        r_gap = ((bit.end_byte + 1) * 8) - bit.sum
        b[0] &= left_bit_gap[l_gap]
        b[-1] &= right_bit_gap[r_gap]
        return int.from_bytes(b) >> r_gap

    @property
    def view(self) -> int:
        return self.get_header(VIEW_BIT)

    @property
    def is_exp(self) -> bool:
        return self.get_header(IS_EXP_BIT) == 1
    
    @property
    def year(self) -> int|None:
        if self.is_exp:
            return self.get_header(YEAR_BIT)
        
    @property
    def month(self) -> int|None:
        if self.is_exp:
            return self.get_header(MONTH_BIT)
    
    @property
    def day(self) -> int|None:
        if self.is_exp:
            return self.get_header(DAY_BIT)
    
    @property
    def hour(self) -> int|None:
        if self.is_exp:
            return self.get_header(HOUR_BIT)
    
    @property
    def minute(self) -> int|None:
        if self.is_exp:
            return self.get_header(MINUTE_BIT)
    
    @property
    def second(self) -> int|None:
        if self.is_exp:
            return self.get_header(SENCOND_BIT)
        
    @property
    def datetime(self) -> datetime.datetime|None:
        if not self.is_exp:
            return None
        return datetime.datetime(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second)
        
    @property
    def url(self) -> str:
        header_lenght = IS_EXP_BIT.end_byte + 1
        if self.is_exp:
            header_lenght = SENCOND_BIT.end_byte + 1
        return self.b[header_lenght:].decode()
    
    @view.setter
    def view(self, n:int):
        is_exp = self.is_exp
        if n > (2 ** VIEW_BIT.lenght - 1):
            raise OverViewError()
        self.b[VIEW_BIT.start_byte:VIEW_BIT.end_byte + 1] = (n << IS_EXP_BIT.lenght).to_bytes(VIEW_BIT.beyt_lenght)
        if is_exp:
            self.b[VIEW_BIT.end_byte] |= left_bit_gap[8 - IS_EXP_BIT.lenght]
    
class UrlCreator():
    def __init__(self) -> None:
        self.view:int = 0
        self.exp:int = 0
        self.year:int|None = None
        self.month:int|None = None
        self.day:int|None = None
        self.hour:int|None = None
        self.minute:int|None = None
        self.second:int|None = None

    def set_date(self, date:str) -> UrlCreator:
        try:
            date:datetime.datetime = datetime.datetime.fromisoformat(date)
        except ValueError:
            raise DateValueError()
        self.year = date.year
        self.month = date.month
        self.day = date.day
        self.hour = date.hour
        self.minute = date.minute
        self.second = date.second
        self.exp = 1
        return self
    
    def create(self, url:str):
        r = 0
        bits_index = 0
        for feild_key in self.__dict__:
            if self.__dict__[feild_key] == None:
                return UrlModel(r.to_bytes(BITS[bits_index - 1].end_byte + 1) + url.encode())
            r <<= BITS[bits_index].lenght
            r += self.__dict__[feild_key]
            bits_index += 1
        return UrlModel(r.to_bytes(BITS[bits_index - 1].end_byte + 1) + url.encode())
    
    def create_byte(self, b: bytes):
        return UrlModel(b)

class DateValueError(Exception):
    """ISO 표준 표기법을 지키니 않아 만료 기간을 알 수 없음"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class OverViewError(Exception):
    """View의 값이 2^32-1을 넘겨 저장 할 수 없음"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# u = UrlCreator().set_date("2024-06-08T15:58:01").create("a")
# print(u.b)
# print(u.view)
# print(u.is_exp)
# print(u.year)
# print(u.month)
# print(u.day)
# print(u.hour)
# print(u.minute)
# print(u.second)
# print(u.url)
# print(u.datetime)

