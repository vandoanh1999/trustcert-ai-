import spacy
import pytest
from services.graph.logic import extract_svo_relations

# Tải mô hình spacy một lần cho tất cả các test
nlp = spacy.load("en_core_web_sm")

def test_extract_svo_relations_simple_sentence():
    """
    Kiểm tra xem hàm có trích xuất được một bộ ba SVO đơn giản hay không.
    """
    text = "Apple is developing a new operating system."
    doc = nlp(text)
    relations = extract_svo_relations(doc)

    assert len(relations) > 0, "Không tìm thấy quan hệ nào"
    assert ("Apple", "developing", "system") in relations, "Không tìm thấy bộ ba SVO mong đợi"

def test_extract_svo_relations_no_relations():
    """
    Kiểm tra xem hàm có trả về danh sách rỗng cho câu không có SVO rõ ràng hay không.
    """
    text = "The weather is nice today."
    doc = nlp(text)
    relations = extract_svo_relations(doc)

    assert len(relations) == 0, "Tìm thấy quan hệ trong khi không nên có"

def test_extract_svo_relations_multiple_sentences():
    """
    Kiểm tra xem hàm có xử lý được nhiều câu hay không.
    """
    text = "Google acquired YouTube in 2006. Microsoft launched Windows 11 recently."
    doc = nlp(text)
    relations = extract_svo_relations(doc)

    assert len(relations) >= 2, "Không tìm thấy đủ số lượng quan hệ"
    assert ("Google", "acquired", "YouTube") in relations
    assert ("Microsoft", "launched", "Windows") in relations

def test_extract_svo_relations_complex_sentence():
    """
    Kiểm tra một câu phức tạp hơn.
    """
    text = "The quick brown fox jumps over the lazy dog."
    doc = nlp(text)
    relations = extract_svo_relations(doc)

    assert ("fox", "jumps", "dog") in relations
