import random
import string

def generate_code(length=10):
    """
    지정한 길이만큼의 랜덤 영문자+숫자 조합 코드를 생성합니다.
    예: '8FJ2KD9LQX'
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

def get_temperament(mbti):
    """
    MBTI 문자열을 입력받아 Temperament(SJ, SP, NF, NT)를 반환
    """
    sj_types = {"ESTJ", "ISTJ", "ESFJ", "ISFJ"}
    sp_types = {"ESTP", "ISTP", "ESFP", "ISFP"}
    nf_types = {"ENFP", "INFP", "ENFJ", "INFJ"}
    nt_types = {"ENTJ", "INTJ", "ENTP", "INTP"}

    if not mbti:
        return ""
    mbti = mbti.upper()
    if mbti in sj_types:
        return "SJ"
    elif mbti in sp_types:
        return "SP"
    elif mbti in nf_types:
        return "NF"
    elif mbti in nt_types:
        return "NT"
    else:
        return ""
