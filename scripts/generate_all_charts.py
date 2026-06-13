"""
Generate all 41 chart types using templates.
Reads each template's {{PLACEHOLDER}} markers first, then fills data.
"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.build_template import build

OUT = os.path.abspath("examples/all_charts")
os.makedirs(OUT, exist_ok=True)
TPL = "references/templates"

# Each entry: (output_name, template_path, data_dict)
CHARTS = []

D = json.dumps  # shortcut

# ═══ Bar ═══
CHARTS.append(("01_Bar_Basic", "bar/basic.html", {
    "TITLE":"01 基础柱状图","CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "VALUES":[{"value": 6500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAilBMVEVHcEyZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWMnaiPn6qZqrVmdX9zgo2Wp7IpLzNwf4mAkJqMnah5iZN8jJeGlqGPoKtsfIaDk52JmaRpeIJ2hpCLm6UwNzs3PkNhbXRFTlRaZWx2hIyTo65vfIRodHySoq3+fuZKAAAAEnRSTlMAMJ+vYN8QQL+AIM+P71Bwv++BmxKZAAACeklEQVR4Xu3X15LbIBSAYUBUNScHyb1vT3n/14vbhj0WCNjkJjP5rz3fiINGBvLP9z/ZmkLDe0LXvCT50bqCYaKmeQwXEEq3uUyYSlyhLCDS1y/6EjNcjTgVRFuBq6oDay0g3mKO3IapoaMgpa4HnFapD4RbLwc2k8gpIane9gOpoWjnIa3jzsNztLK0dlsYl5pEaGE3Pom6EaVmdz5ISLf5iW2PXp/dIJMMdVvwpq5QnQ5ZP6SvkP5jCMpMaGsXfqi+QMIBzy8vzxDOuv3HiQvknNfpqdeR98hCIIqh6aWfIWgehiY+6CE8oi4EMQw9nZ2nkZWtQlCFobfH6fTxLbz5dg+hMAQP338EF7a39gDBqIMi9Qe3ssC0U99qa7+FoSIVWp6cOYQTDoo6hx5GKglJdOwexmoToM3s7KxgNBOFvi3tuRmMpyPQ/srYWR+BRPhPZLOYHw/2WtdDrMGHrV92XTezqBXEU/fQzt43W0A+VMH6nllDUgb/ixiA2UdltQFIhQy4hAKA9fzaegEZFQgqCHw2TRRaaPV3IO4mlhM7A0SiPeSQX6UuEEFQCflNblCFvuEiH5I3SCOIZTsFuUE1gtpsqH2HJgiSuU5D3iHlIEncyFJjt2Moegb1iSG11zNWhTaKnyCeu7JTknOJTuzsBNHclbkmjj+7eRAnLopPgzoLQndUgcZdDAHRBCF8M0YXAjOETPCSUBEUc1KRB2kMSe0kGoaoF8LVDuLB2wbxH4xw9DZj5vskyRtUeY5qw0putFG+n2v8xuHdH0kFL4lS+IYXDk+p4R8GgCVGIpWs+c0w9PTSOKpoSUJUcWO4op5ZqtaYiVIE9wvKcRFj0cNHIgAAAABJRU5ErkJggg=="}, {"value": 3500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEx0g46ZqrXM1t21w8uElJ/M1t2sucGZqrWZqrWZqrVmdX9od4HM1t2ZqrXM1t2ZqrXM1t3M1t1mdX+ZqrWZqrWwvsfM1t3M1t2ZqrWZqrXM1t3M1t2ZqrVndoBmdX9mdX/F0NjM1t1mdX+BkZyImKOvvcZ+jZiZqrXM1t1mdX/mqqqOn6qTo66GlqB+jpgpLzPVqq2Wp7JvfoinqrPIqq+0qrKdrrm7yNCntsBFTlTI0tpVYGe9qrA+RkthbXRsnZ8YAAAAKHRSTlMA/oCAMCOfEEC/n8Ng79+/YM8ghu+PSN9gz3CvUK/vr0p4j5+Iv9/PYy3u2QAAAuFJREFUeF6l1Glb4jAQwPFpaWmBgtwoKN67k/Ti9t79/t9qGxOY1aok6f99f89kQgDzvGbj/v7uKgDjBi3OW61B5Etoiu9lvyNTK5pzWSsSUHCGstQZGFL+gO8pX0gdfFtuN2Kq+RWYdcn3RfJwcRwvCypZ35pBYiSSQsRlXLRFXPFbY4ikLuI2VlLCB2ZHo+a+Kycq2iHmPAqLNKEWp3irgZtYtkRM+RqLbCC+EgPJNogOTyyhNWK8702cLdOHLknJUiRIrDvjuT4UKSZPUERHWxpCwfydWaFqRxDmJhBcEaNGIoiWrdNdihTS/RveWnCBn9odbm3NUUJe+/yYMx4ifi1tELmjoAk7OeK4+FWbbbzciceWSchjbPKz08SfyngqoRpjLADKC4wcdByUUK+ATskJ2jUjJ+WZhAJWNCPonE1MHMwdCcKYifoHqCbmo7pHnCRfKajGRHScG8batCUPdYM6E9G3JwVbB1XQ0YbEh6I6QbR8GKF2MGEy7wCRFKJ+wFQ9WvZeCjo2EKsRJLoJYIRWEBur35Fqco2WULsvII/kJ0uI9QIhtatD8u9kdoAebCD6NZ0y1SPaQCQFbTqZDURS3WYghJ4SaON9iw3RW6N6fTHSizxY+rpYLF5Tvdf/ufb5y97B54Xoj4YENVbuUTHoLGRcAxoTQKHqr4KeNaA+K/diA8Gk7DyixdFgVobo5g2WTU+i/FjV9T9rXT8t6Zs3lqFWANArHcwogq4/Ok9oCwWlBVlCUK/mEORVcwiCGe2nGtRX9/5g75zBe79oHMu6EsKHJ5qmwkCAFRt6FSE6mKqDqiRJqjhwoZg159wxpYZjODRF0YrLcrM9e0B5ciCuMpnJJYWWlGT5WkCZNtPw4WMj3JcVUKrLhPA5Hw+tEk2nWWLo3vTruD58WWh04TRMhZE6oxB+yh/qIM2uD8eaHrui0dgHrdzhd0TTDX0wKXRHjcaZ+rrIdadhqAn8A87BQoMTVo0lAAAAAElFTkSuQmCC"}, {"value": 3000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAnFBMVEVHcEyaqrWaqrSZqrWaqrSaqrWaqrWaqrWaqrSaqrSaqrSaqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrVibXQpLzN9jJZtfIaHlqBndX+Uo61wf4mAkJqXp7F6iZN0goyQoKqEk52aqrVqeIJ3hpCKmaONnaeXprBufYe5w8qLlp7Z4OT1+PrS19ucpq2xvsaltL3I0df7ApL7AAAAK3RSTlMAMEC//48QgHDvn8/fryDvcED/n2BQ/////////////////////////+/fbmjbTAAAAdJJREFUeAHt04WO6zAQheHjesI85c4yM77/u900V0VrFXsZ8okLv3JcF52v0ul0Op2O6ql3yWgi8vBafhD6/zsR1SK8VkyUNKWU5jReKyOiIA91QkRxUnhBEJRVpRZzqzLIdMoN3S9zvCj3UopogVcKXbApGeBFA1rDrdKhRceqxJ5Fx67Uh6lHNBqPR44lY11zecY1cisVPjblCRkhq1KAdSqOiIxpVqEUNT/W8bAXximZrEuq+VMY3EMl4NNkOntzKANCEpGdt4Y0ENGuyN5bQwxFtH9wePT2UEim/ePDjfQJtykYARmOpiJy7HYhGZnZOZWzHcdhlYY2dk1lRo4drirzOp7JAbmHYJzRuUz3nTusALU17FQu3DuMmqZ1BzJ5RSdFTV2uTZltDWM7GeauTs9XHTl6RYdL1NRM5LBJHR2IzF7T4Ry1Hl3fSN06nIpML17V0WhEt3f3D4d15cy8iHYqNILHu7u7J9rGTg/UCJ6er42M9lK2pLDQS2hTMvABP2ErfaxRYaajRcVTaOSF5U/Wqm/3QO0qtjBEu5wtVG5PpNO3hAa8BKhBkOl5L9E6GIIXBnA6bGxzOuzUJlSgHduE+DNDg8W21DzRKis23voHkmGCCGZlkZ0AAAAASUVORK5CYII="}, {"value": 2000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAjVBMVEVHcEwxNz0xNz0xNz0xNz2ZqrUxNz0xNz0xNz0xNz0xNz0xNz0xNz2ZqrWZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrUxNz2ZqrX///9FTVQ4PkWYm56To65LVFt/jZeMnKZyf4hlcXlseIFYYmpfaXJSW2OBJucVAAAAH3RSTlMA71DPr78ggBBA359ggEAwn78QcFCPYN+vj+8wIM9wM29S9wAAAdhJREFUeNrt1Ol22jAQhuGRF3nFxmxJun0GsjTpcv+X1xKJDoJjSbb8r3n+cYDXo7GBPnz4b6w2i/s0vV80FKRZ9md3u4BpHvpLy9XUztfetKRp0tN3NyuizfmA0073ue/TL6Ts9J5oit2nb/xCz9RQqIUKLShUGh7ik4WHmrQPDa2aZvNwpyuTli3rqgNee9MTbJKCrtUxTg79lTfYJbmRyWMoz9cDHeEQ52ZnIPQMp4RYhrOj2fkJDwUPJKCZy/5+gI/KHEg7Pv3L/IIfIXVHClw4vJwqLz9+w99ahSq8e9zvHzEelySU/V+YShJREhTihRdA+NFQ6oHCEWEe1M4VKuYK5Qgm1I4EQnUqVM0VknOFaItAmQ5RNleI8uJdtC0xRaRChqjDeIUOmYrxUxGHDJnAKPFQiGSMMbqB0Oj7mFlCox73yBaS8NfaQtTBG1lDtf+u7aEcvrb2ECXwFOlQ8NmkDoWerSQOuc5W0g0OVc7Qmu+LLRQ5Q/LiN3CjxFnuDPGHC8vzmuifZkbDKmi299bkVvNFb2R885nrAajpVsQX8RDzOq+1fBEPW8tFVUeQE88fWf5mMvLDj/XAtiX5SYa30OqBvM8WW/5Cy5x8xaKlAa0w3/sDh78rWpS3Kr8AAAAASUVORK5CYII="}, {"value": 1800, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEz/zE37tDT0kAz/zE3/zE12TCn+y0z0kAx1TCl1TCn/zE15Tih1TCn0kAz1kg7/zE30kAz+ykt1TCn/zE31kg7yjwz0kAz/zE11TCl1TCl1TCl4TSj1lBHyjgz3oB7/zE30kAx1TCn/zE3ywEmcZym6jDt1TCn/zE30kAz+x0f5pyT1lRD7szL8vDv3nRn9wUGNYC1/USbDdhf0w0vks0Wybx4rMTPcgxHNoUOtgjmDcj7qiw7OfBTkuEqZXyF8bTsrAAAAJ3RSTlMAvyBmYIDZQL8UgBBgQRDP30DvcDChgDCZpjC/79+PUM/vj69wv4DzeXUBAAADgElEQVR4XqWX63biOAyAHUigCeVOKXQo7XRmV5Jz49p7Z9//rRZr7DbjTkOIv1899JwPSZYtISzuYBGGLZgLVxYA3S4ACDHx/YmDCLRo4uGBmbPoGWUcSxzV1TRm+x0yWUKU4W1NT4DvpDklEoNams4MEXcvD7BjE6U46tTJyh/ggeeHh4cXJYozxJuTYwkGqHnRIsVPcSoevvPrIHpizX59d6pnggV2T7/YI5+hdaqojZ+JaQtwdWqd8RMp0SPAWJyIP0KLhIigztX18Q9WdOA/LpKbSSrRPUBYp6/bCn/wkdobwLmoTeeWRRkRvQLcifpMcqIklquYaA3fhAMXdCCX6t4BuIguSREj4hNA18V0zSaJuAOInHOjDBHX0HIRNbWIcwsdRA2TGu5VJzmgi825OU3KM338KO/dcrtIUvasEnNL3KaSTIg2TufmIxPzU+ISUvuPF6DlLCLFxqW7GwXRI7g8AcjkbNpu5q6ilJjX5bDnJuKQmBwHnncxnTaVsoZIskm3eUZMv3mqiEnjPI9THV6Bs+VlVZGNJIvrZj1RVnAkCXFYvTqiVUGUm3r1Kq459jZgiLH/XZuqXBGZmjqbK2zIMBBNVi0riFIzlaxe4M88IS7Z1DgqMgGsbBO7PTP/Lo6JMtJwcsWuksgiM7Z6R0TxRz1stEhPm/INunBGEv/GSCj62/vttFSUvoty/DvKE7YAYFG2sA4TqVNL5BeizkH0DRRlw+GG4lWir/0XtIUIgSkbDlOilUzjNMMv8YUYa9Fd2TrCtZH4NYEQETBlT3qfG7GUHx8RzassEei1A2+EnxkIcXW0RsPief3enP0g8DxvlMnCsZlTC48sWikyDWtLMSm3K/TRkiO6RqZdFBW+IFAdOY7GYel6pGgiE1gik7MnjkPM0NPHY4n0MYyqrpDUm7Ho1moLoumITZOjohv2fDdb0udQf+jePsaURWdmBEysnwTUCFg0q7CKKqZmKPlWW5CeDYOKvyCaQtzqY7ND7ZgOK6enKyHEzDrnM9ITaFCpSENiDsqfJgU71FmlIs03WzVD1QzYmVvFjDf3rxxq4RtKGAPA+pHnVQTr5ydzSfiyb954/swP/9gjlnrCBRzYPKqdpQVKuueimru+7Zs3dl3e211g/uEQzJ8MMItLIc6B+VeUcjWOonFXGFErCk2s51EUnYdCi1r2e/Y/5JIVQn2w47EAAAAASUVORK5CYII="}],"ROTATE":0}))

CHARTS.append(("02_Bar_Horizontal", "bar/horizontal.html", {
    "TITLE":"02 横向柱状图","CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "VALUES":[{"value": 6500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAilBMVEVHcEyZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWMnaiPn6qZqrVmdX9zgo2Wp7IpLzNwf4mAkJqMnah5iZN8jJeGlqGPoKtsfIaDk52JmaRpeIJ2hpCLm6UwNzs3PkNhbXRFTlRaZWx2hIyTo65vfIRodHySoq3+fuZKAAAAEnRSTlMAMJ+vYN8QQL+AIM+P71Bwv++BmxKZAAACeklEQVR4Xu3X15LbIBSAYUBUNScHyb1vT3n/14vbhj0WCNjkJjP5rz3fiINGBvLP9z/ZmkLDe0LXvCT50bqCYaKmeQwXEEq3uUyYSlyhLCDS1y/6EjNcjTgVRFuBq6oDay0g3mKO3IapoaMgpa4HnFapD4RbLwc2k8gpIane9gOpoWjnIa3jzsNztLK0dlsYl5pEaGE3Pom6EaVmdz5ISLf5iW2PXp/dIJMMdVvwpq5QnQ5ZP6SvkP5jCMpMaGsXfqi+QMIBzy8vzxDOuv3HiQvknNfpqdeR98hCIIqh6aWfIWgehiY+6CE8oi4EMQw9nZ2nkZWtQlCFobfH6fTxLbz5dg+hMAQP338EF7a39gDBqIMi9Qe3ssC0U99qa7+FoSIVWp6cOYQTDoo6hx5GKglJdOwexmoToM3s7KxgNBOFvi3tuRmMpyPQ/srYWR+BRPhPZLOYHw/2WtdDrMGHrV92XTezqBXEU/fQzt43W0A+VMH6nllDUgb/ixiA2UdltQFIhQy4hAKA9fzaegEZFQgqCHw2TRRaaPV3IO4mlhM7A0SiPeSQX6UuEEFQCflNblCFvuEiH5I3SCOIZTsFuUE1gtpsqH2HJgiSuU5D3iHlIEncyFJjt2Moegb1iSG11zNWhTaKnyCeu7JTknOJTuzsBNHclbkmjj+7eRAnLopPgzoLQndUgcZdDAHRBCF8M0YXAjOETPCSUBEUc1KRB2kMSe0kGoaoF8LVDuLB2wbxH4xw9DZj5vskyRtUeY5qw0putFG+n2v8xuHdH0kFL4lS+IYXDk+p4R8GgCVGIpWs+c0w9PTSOKpoSUJUcWO4op5ZqtaYiVIE9wvKcRFj0cNHIgAAAABJRU5ErkJggg=="}, {"value": 3500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEx0g46ZqrXM1t21w8uElJ/M1t2sucGZqrWZqrWZqrVmdX9od4HM1t2ZqrXM1t2ZqrXM1t3M1t1mdX+ZqrWZqrWwvsfM1t3M1t2ZqrWZqrXM1t3M1t2ZqrVndoBmdX9mdX/F0NjM1t1mdX+BkZyImKOvvcZ+jZiZqrXM1t1mdX/mqqqOn6qTo66GlqB+jpgpLzPVqq2Wp7JvfoinqrPIqq+0qrKdrrm7yNCntsBFTlTI0tpVYGe9qrA+RkthbXRsnZ8YAAAAKHRSTlMA/oCAMCOfEEC/n8Ng79+/YM8ghu+PSN9gz3CvUK/vr0p4j5+Iv9/PYy3u2QAAAuFJREFUeF6l1Glb4jAQwPFpaWmBgtwoKN67k/Ti9t79/t9qGxOY1aok6f99f89kQgDzvGbj/v7uKgDjBi3OW61B5Etoiu9lvyNTK5pzWSsSUHCGstQZGFL+gO8pX0gdfFtuN2Kq+RWYdcn3RfJwcRwvCypZ35pBYiSSQsRlXLRFXPFbY4ikLuI2VlLCB2ZHo+a+Kycq2iHmPAqLNKEWp3irgZtYtkRM+RqLbCC+EgPJNogOTyyhNWK8702cLdOHLknJUiRIrDvjuT4UKSZPUERHWxpCwfydWaFqRxDmJhBcEaNGIoiWrdNdihTS/RveWnCBn9odbm3NUUJe+/yYMx4ifi1tELmjoAk7OeK4+FWbbbzciceWSchjbPKz08SfyngqoRpjLADKC4wcdByUUK+ATskJ2jUjJ+WZhAJWNCPonE1MHMwdCcKYifoHqCbmo7pHnCRfKajGRHScG8batCUPdYM6E9G3JwVbB1XQ0YbEh6I6QbR8GKF2MGEy7wCRFKJ+wFQ9WvZeCjo2EKsRJLoJYIRWEBur35Fqco2WULsvII/kJ0uI9QIhtatD8u9kdoAebCD6NZ0y1SPaQCQFbTqZDURS3WYghJ4SaON9iw3RW6N6fTHSizxY+rpYLF5Tvdf/ufb5y97B54Xoj4YENVbuUTHoLGRcAxoTQKHqr4KeNaA+K/diA8Gk7DyixdFgVobo5g2WTU+i/FjV9T9rXT8t6Zs3lqFWANArHcwogq4/Ok9oCwWlBVlCUK/mEORVcwiCGe2nGtRX9/5g75zBe79oHMu6EsKHJ5qmwkCAFRt6FSE6mKqDqiRJqjhwoZg159wxpYZjODRF0YrLcrM9e0B5ciCuMpnJJYWWlGT5WkCZNtPw4WMj3JcVUKrLhPA5Hw+tEk2nWWLo3vTruD58WWh04TRMhZE6oxB+yh/qIM2uD8eaHrui0dgHrdzhd0TTDX0wKXRHjcaZ+rrIdadhqAn8A87BQoMTVo0lAAAAAElFTkSuQmCC"}, {"value": 3000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAnFBMVEVHcEyaqrWaqrSZqrWaqrSaqrWaqrWaqrWaqrSaqrSaqrSaqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrVibXQpLzN9jJZtfIaHlqBndX+Uo61wf4mAkJqXp7F6iZN0goyQoKqEk52aqrVqeIJ3hpCKmaONnaeXprBufYe5w8qLlp7Z4OT1+PrS19ucpq2xvsaltL3I0df7ApL7AAAAK3RSTlMAMEC//48QgHDvn8/fryDvcED/n2BQ/////////////////////////+/fbmjbTAAAAdJJREFUeAHt04WO6zAQheHjesI85c4yM77/u900V0VrFXsZ8okLv3JcF52v0ul0Op2O6ql3yWgi8vBafhD6/zsR1SK8VkyUNKWU5jReKyOiIA91QkRxUnhBEJRVpRZzqzLIdMoN3S9zvCj3UopogVcKXbApGeBFA1rDrdKhRceqxJ5Fx67Uh6lHNBqPR44lY11zecY1cisVPjblCRkhq1KAdSqOiIxpVqEUNT/W8bAXximZrEuq+VMY3EMl4NNkOntzKANCEpGdt4Y0ENGuyN5bQwxFtH9wePT2UEim/ePDjfQJtykYARmOpiJy7HYhGZnZOZWzHcdhlYY2dk1lRo4drirzOp7JAbmHYJzRuUz3nTusALU17FQu3DuMmqZ1BzJ5RSdFTV2uTZltDWM7GeauTs9XHTl6RYdL1NRM5LBJHR2IzF7T4Ry1Hl3fSN06nIpML17V0WhEt3f3D4d15cy8iHYqNILHu7u7J9rGTg/UCJ6er42M9lK2pLDQS2hTMvABP2ErfaxRYaajRcVTaOSF5U/Wqm/3QO0qtjBEu5wtVG5PpNO3hAa8BKhBkOl5L9E6GIIXBnA6bGxzOuzUJlSgHduE+DNDg8W21DzRKis23voHkmGCCGZlkZ0AAAAASUVORK5CYII="}, {"value": 2000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAjVBMVEVHcEwxNz0xNz0xNz0xNz2ZqrUxNz0xNz0xNz0xNz0xNz0xNz0xNz2ZqrWZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrUxNz2ZqrX///9FTVQ4PkWYm56To65LVFt/jZeMnKZyf4hlcXlseIFYYmpfaXJSW2OBJucVAAAAH3RSTlMA71DPr78ggBBA359ggEAwn78QcFCPYN+vj+8wIM9wM29S9wAAAdhJREFUeNrt1Ol22jAQhuGRF3nFxmxJun0GsjTpcv+X1xKJDoJjSbb8r3n+cYDXo7GBPnz4b6w2i/s0vV80FKRZ9md3u4BpHvpLy9XUztfetKRp0tN3NyuizfmA0073ue/TL6Ts9J5oit2nb/xCz9RQqIUKLShUGh7ik4WHmrQPDa2aZvNwpyuTli3rqgNee9MTbJKCrtUxTg79lTfYJbmRyWMoz9cDHeEQ52ZnIPQMp4RYhrOj2fkJDwUPJKCZy/5+gI/KHEg7Pv3L/IIfIXVHClw4vJwqLz9+w99ahSq8e9zvHzEelySU/V+YShJREhTihRdA+NFQ6oHCEWEe1M4VKuYK5Qgm1I4EQnUqVM0VknOFaItAmQ5RNleI8uJdtC0xRaRChqjDeIUOmYrxUxGHDJnAKPFQiGSMMbqB0Oj7mFlCox73yBaS8NfaQtTBG1lDtf+u7aEcvrb2ECXwFOlQ8NmkDoWerSQOuc5W0g0OVc7Qmu+LLRQ5Q/LiN3CjxFnuDPGHC8vzmuifZkbDKmi299bkVvNFb2R885nrAajpVsQX8RDzOq+1fBEPW8tFVUeQE88fWf5mMvLDj/XAtiX5SYa30OqBvM8WW/5Cy5x8xaKlAa0w3/sDh78rWpS3Kr8AAAAASUVORK5CYII="}, {"value": 1800, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEz/zE37tDT0kAz/zE3/zE12TCn+y0z0kAx1TCl1TCn/zE15Tih1TCn0kAz1kg7/zE30kAz+ykt1TCn/zE31kg7yjwz0kAz/zE11TCl1TCl1TCl4TSj1lBHyjgz3oB7/zE30kAx1TCn/zE3ywEmcZym6jDt1TCn/zE30kAz+x0f5pyT1lRD7szL8vDv3nRn9wUGNYC1/USbDdhf0w0vks0Wybx4rMTPcgxHNoUOtgjmDcj7qiw7OfBTkuEqZXyF8bTsrAAAAJ3RSTlMAvyBmYIDZQL8UgBBgQRDP30DvcDChgDCZpjC/79+PUM/vj69wv4DzeXUBAAADgElEQVR4XqWX63biOAyAHUigCeVOKXQo7XRmV5Jz49p7Z9//rRZr7DbjTkOIv1899JwPSZYtISzuYBGGLZgLVxYA3S4ACDHx/YmDCLRo4uGBmbPoGWUcSxzV1TRm+x0yWUKU4W1NT4DvpDklEoNams4MEXcvD7BjE6U46tTJyh/ggeeHh4cXJYozxJuTYwkGqHnRIsVPcSoevvPrIHpizX59d6pnggV2T7/YI5+hdaqojZ+JaQtwdWqd8RMp0SPAWJyIP0KLhIigztX18Q9WdOA/LpKbSSrRPUBYp6/bCn/wkdobwLmoTeeWRRkRvQLcifpMcqIklquYaA3fhAMXdCCX6t4BuIguSREj4hNA18V0zSaJuAOInHOjDBHX0HIRNbWIcwsdRA2TGu5VJzmgi825OU3KM338KO/dcrtIUvasEnNL3KaSTIg2TufmIxPzU+ISUvuPF6DlLCLFxqW7GwXRI7g8AcjkbNpu5q6ilJjX5bDnJuKQmBwHnncxnTaVsoZIskm3eUZMv3mqiEnjPI9THV6Bs+VlVZGNJIvrZj1RVnAkCXFYvTqiVUGUm3r1Kq459jZgiLH/XZuqXBGZmjqbK2zIMBBNVi0riFIzlaxe4M88IS7Z1DgqMgGsbBO7PTP/Lo6JMtJwcsWuksgiM7Z6R0TxRz1stEhPm/INunBGEv/GSCj62/vttFSUvoty/DvKE7YAYFG2sA4TqVNL5BeizkH0DRRlw+GG4lWir/0XtIUIgSkbDlOilUzjNMMv8YUYa9Fd2TrCtZH4NYEQETBlT3qfG7GUHx8RzassEei1A2+EnxkIcXW0RsPief3enP0g8DxvlMnCsZlTC48sWikyDWtLMSm3K/TRkiO6RqZdFBW+IFAdOY7GYel6pGgiE1gik7MnjkPM0NPHY4n0MYyqrpDUm7Ho1moLoumITZOjohv2fDdb0udQf+jePsaURWdmBEysnwTUCFg0q7CKKqZmKPlWW5CeDYOKvyCaQtzqY7ND7ZgOK6enKyHEzDrnM9ITaFCpSENiDsqfJgU71FmlIs03WzVD1QzYmVvFjDf3rxxq4RtKGAPA+pHnVQTr5ydzSfiyb954/swP/9gjlnrCBRzYPKqdpQVKuueimru+7Zs3dl3e211g/uEQzJ8MMItLIc6B+VeUcjWOonFXGFErCk2s51EUnYdCi1r2e/Y/5JIVQn2w47EAAAAASUVORK5CYII="}],"ROTATE":0}))

CHARTS.append(("03_Bar_Stacked", "bar/stack.html", {
    "TITLE":"03 堆叠柱状图","CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "SERIES":D([{"name":"Email","type":"bar","stack":"x","data":[120,132,101,134,90,230,210]},
                {"name":"Union Ads","type":"bar","stack":"x","data":[220,182,191,234,290,330,310]},
                {"name":"Video Ads","type":"bar","stack":"x","data":[150,232,201,154,190,330,410]}])}))

CHARTS.append(("04_Bar_Waterfall", "bar/waterfall.html", {
    "TITLE":"04 瀑布图","CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "INCREASE":D([120,200,150,80,0,0,260]),"DECREASE":D([0,0,0,0,110,60,0])}))

CHARTS.append(("05_Bar_Race", "bar/race.html", {
    "TITLE":"05 动态排序","VALUES":[{"value": 6500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAilBMVEVHcEyZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWMnaiPn6qZqrVmdX9zgo2Wp7IpLzNwf4mAkJqMnah5iZN8jJeGlqGPoKtsfIaDk52JmaRpeIJ2hpCLm6UwNzs3PkNhbXRFTlRaZWx2hIyTo65vfIRodHySoq3+fuZKAAAAEnRSTlMAMJ+vYN8QQL+AIM+P71Bwv++BmxKZAAACeklEQVR4Xu3X15LbIBSAYUBUNScHyb1vT3n/14vbhj0WCNjkJjP5rz3fiINGBvLP9z/ZmkLDe0LXvCT50bqCYaKmeQwXEEq3uUyYSlyhLCDS1y/6EjNcjTgVRFuBq6oDay0g3mKO3IapoaMgpa4HnFapD4RbLwc2k8gpIane9gOpoWjnIa3jzsNztLK0dlsYl5pEaGE3Pom6EaVmdz5ISLf5iW2PXp/dIJMMdVvwpq5QnQ5ZP6SvkP5jCMpMaGsXfqi+QMIBzy8vzxDOuv3HiQvknNfpqdeR98hCIIqh6aWfIWgehiY+6CE8oi4EMQw9nZ2nkZWtQlCFobfH6fTxLbz5dg+hMAQP338EF7a39gDBqIMi9Qe3ssC0U99qa7+FoSIVWp6cOYQTDoo6hx5GKglJdOwexmoToM3s7KxgNBOFvi3tuRmMpyPQ/srYWR+BRPhPZLOYHw/2WtdDrMGHrV92XTezqBXEU/fQzt43W0A+VMH6nllDUgb/ixiA2UdltQFIhQy4hAKA9fzaegEZFQgqCHw2TRRaaPV3IO4mlhM7A0SiPeSQX6UuEEFQCflNblCFvuEiH5I3SCOIZTsFuUE1gtpsqH2HJgiSuU5D3iHlIEncyFJjt2Moegb1iSG11zNWhTaKnyCeu7JTknOJTuzsBNHclbkmjj+7eRAnLopPgzoLQndUgcZdDAHRBCF8M0YXAjOETPCSUBEUc1KRB2kMSe0kGoaoF8LVDuLB2wbxH4xw9DZj5vskyRtUeY5qw0putFG+n2v8xuHdH0kFL4lS+IYXDk+p4R8GgCVGIpWs+c0w9PTSOKpoSUJUcWO4op5ZqtaYiVIE9wvKcRFj0cNHIgAAAABJRU5ErkJggg=="}, {"value": 3500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEx0g46ZqrXM1t21w8uElJ/M1t2sucGZqrWZqrWZqrVmdX9od4HM1t2ZqrXM1t2ZqrXM1t3M1t1mdX+ZqrWZqrWwvsfM1t3M1t2ZqrWZqrXM1t3M1t2ZqrVndoBmdX9mdX/F0NjM1t1mdX+BkZyImKOvvcZ+jZiZqrXM1t1mdX/mqqqOn6qTo66GlqB+jpgpLzPVqq2Wp7JvfoinqrPIqq+0qrKdrrm7yNCntsBFTlTI0tpVYGe9qrA+RkthbXRsnZ8YAAAAKHRSTlMA/oCAMCOfEEC/n8Ng79+/YM8ghu+PSN9gz3CvUK/vr0p4j5+Iv9/PYy3u2QAAAuFJREFUeF6l1Glb4jAQwPFpaWmBgtwoKN67k/Ti9t79/t9qGxOY1aok6f99f89kQgDzvGbj/v7uKgDjBi3OW61B5Etoiu9lvyNTK5pzWSsSUHCGstQZGFL+gO8pX0gdfFtuN2Kq+RWYdcn3RfJwcRwvCypZ35pBYiSSQsRlXLRFXPFbY4ikLuI2VlLCB2ZHo+a+Kycq2iHmPAqLNKEWp3irgZtYtkRM+RqLbCC+EgPJNogOTyyhNWK8702cLdOHLknJUiRIrDvjuT4UKSZPUERHWxpCwfydWaFqRxDmJhBcEaNGIoiWrdNdihTS/RveWnCBn9odbm3NUUJe+/yYMx4ifi1tELmjoAk7OeK4+FWbbbzciceWSchjbPKz08SfyngqoRpjLADKC4wcdByUUK+ATskJ2jUjJ+WZhAJWNCPonE1MHMwdCcKYifoHqCbmo7pHnCRfKajGRHScG8batCUPdYM6E9G3JwVbB1XQ0YbEh6I6QbR8GKF2MGEy7wCRFKJ+wFQ9WvZeCjo2EKsRJLoJYIRWEBur35Fqco2WULsvII/kJ0uI9QIhtatD8u9kdoAebCD6NZ0y1SPaQCQFbTqZDURS3WYghJ4SaON9iw3RW6N6fTHSizxY+rpYLF5Tvdf/ufb5y97B54Xoj4YENVbuUTHoLGRcAxoTQKHqr4KeNaA+K/diA8Gk7DyixdFgVobo5g2WTU+i/FjV9T9rXT8t6Zs3lqFWANArHcwogq4/Ok9oCwWlBVlCUK/mEORVcwiCGe2nGtRX9/5g75zBe79oHMu6EsKHJ5qmwkCAFRt6FSE6mKqDqiRJqjhwoZg159wxpYZjODRF0YrLcrM9e0B5ciCuMpnJJYWWlGT5WkCZNtPw4WMj3JcVUKrLhPA5Hw+tEk2nWWLo3vTruD58WWh04TRMhZE6oxB+yh/qIM2uD8eaHrui0dgHrdzhd0TTDX0wKXRHjcaZ+rrIdadhqAn8A87BQoMTVo0lAAAAAElFTkSuQmCC"}, {"value": 3000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAnFBMVEVHcEyaqrWaqrSZqrWaqrSaqrWaqrWaqrWaqrSaqrSaqrSaqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrVibXQpLzN9jJZtfIaHlqBndX+Uo61wf4mAkJqXp7F6iZN0goyQoKqEk52aqrVqeIJ3hpCKmaONnaeXprBufYe5w8qLlp7Z4OT1+PrS19ucpq2xvsaltL3I0df7ApL7AAAAK3RSTlMAMEC//48QgHDvn8/fryDvcED/n2BQ/////////////////////////+/fbmjbTAAAAdJJREFUeAHt04WO6zAQheHjesI85c4yM77/u900V0VrFXsZ8okLv3JcF52v0ul0Op2O6ql3yWgi8vBafhD6/zsR1SK8VkyUNKWU5jReKyOiIA91QkRxUnhBEJRVpRZzqzLIdMoN3S9zvCj3UopogVcKXbApGeBFA1rDrdKhRceqxJ5Fx67Uh6lHNBqPR44lY11zecY1cisVPjblCRkhq1KAdSqOiIxpVqEUNT/W8bAXximZrEuq+VMY3EMl4NNkOntzKANCEpGdt4Y0ENGuyN5bQwxFtH9wePT2UEim/ePDjfQJtykYARmOpiJy7HYhGZnZOZWzHcdhlYY2dk1lRo4drirzOp7JAbmHYJzRuUz3nTusALU17FQu3DuMmqZ1BzJ5RSdFTV2uTZltDWM7GeauTs9XHTl6RYdL1NRM5LBJHR2IzF7T4Ry1Hl3fSN06nIpML17V0WhEt3f3D4d15cy8iHYqNILHu7u7J9rGTg/UCJ6er42M9lK2pLDQS2hTMvABP2ErfaxRYaajRcVTaOSF5U/Wqm/3QO0qtjBEu5wtVG5PpNO3hAa8BKhBkOl5L9E6GIIXBnA6bGxzOuzUJlSgHduE+DNDg8W21DzRKis23voHkmGCCGZlkZ0AAAAASUVORK5CYII="}, {"value": 2000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAjVBMVEVHcEwxNz0xNz0xNz0xNz2ZqrUxNz0xNz0xNz0xNz0xNz0xNz0xNz2ZqrWZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrUxNz2ZqrX///9FTVQ4PkWYm56To65LVFt/jZeMnKZyf4hlcXlseIFYYmpfaXJSW2OBJucVAAAAH3RSTlMA71DPr78ggBBA359ggEAwn78QcFCPYN+vj+8wIM9wM29S9wAAAdhJREFUeNrt1Ol22jAQhuGRF3nFxmxJun0GsjTpcv+X1xKJDoJjSbb8r3n+cYDXo7GBPnz4b6w2i/s0vV80FKRZ9md3u4BpHvpLy9XUztfetKRp0tN3NyuizfmA0073ue/TL6Ts9J5oit2nb/xCz9RQqIUKLShUGh7ik4WHmrQPDa2aZvNwpyuTli3rqgNee9MTbJKCrtUxTg79lTfYJbmRyWMoz9cDHeEQ52ZnIPQMp4RYhrOj2fkJDwUPJKCZy/5+gI/KHEg7Pv3L/IIfIXVHClw4vJwqLz9+w99ahSq8e9zvHzEelySU/V+YShJREhTihRdA+NFQ6oHCEWEe1M4VKuYK5Qgm1I4EQnUqVM0VknOFaItAmQ5RNleI8uJdtC0xRaRChqjDeIUOmYrxUxGHDJnAKPFQiGSMMbqB0Oj7mFlCox73yBaS8NfaQtTBG1lDtf+u7aEcvrb2ECXwFOlQ8NmkDoWerSQOuc5W0g0OVc7Qmu+LLRQ5Q/LiN3CjxFnuDPGHC8vzmuifZkbDKmi299bkVvNFb2R885nrAajpVsQX8RDzOq+1fBEPW8tFVUeQE88fWf5mMvLDj/XAtiX5SYa30OqBvM8WW/5Cy5x8xaKlAa0w3/sDh78rWpS3Kr8AAAAASUVORK5CYII="}, {"value": 1800, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEz/zE37tDT0kAz/zE3/zE12TCn+y0z0kAx1TCl1TCn/zE15Tih1TCn0kAz1kg7/zE30kAz+ykt1TCn/zE31kg7yjwz0kAz/zE11TCl1TCl1TCl4TSj1lBHyjgz3oB7/zE30kAx1TCn/zE3ywEmcZym6jDt1TCn/zE30kAz+x0f5pyT1lRD7szL8vDv3nRn9wUGNYC1/USbDdhf0w0vks0Wybx4rMTPcgxHNoUOtgjmDcj7qiw7OfBTkuEqZXyF8bTsrAAAAJ3RSTlMAvyBmYIDZQL8UgBBgQRDP30DvcDChgDCZpjC/79+PUM/vj69wv4DzeXUBAAADgElEQVR4XqWX63biOAyAHUigCeVOKXQo7XRmV5Jz49p7Z9//rRZr7DbjTkOIv1899JwPSZYtISzuYBGGLZgLVxYA3S4ACDHx/YmDCLRo4uGBmbPoGWUcSxzV1TRm+x0yWUKU4W1NT4DvpDklEoNams4MEXcvD7BjE6U46tTJyh/ggeeHh4cXJYozxJuTYwkGqHnRIsVPcSoevvPrIHpizX59d6pnggV2T7/YI5+hdaqojZ+JaQtwdWqd8RMp0SPAWJyIP0KLhIigztX18Q9WdOA/LpKbSSrRPUBYp6/bCn/wkdobwLmoTeeWRRkRvQLcifpMcqIklquYaA3fhAMXdCCX6t4BuIguSREj4hNA18V0zSaJuAOInHOjDBHX0HIRNbWIcwsdRA2TGu5VJzmgi825OU3KM338KO/dcrtIUvasEnNL3KaSTIg2TufmIxPzU+ISUvuPF6DlLCLFxqW7GwXRI7g8AcjkbNpu5q6ilJjX5bDnJuKQmBwHnncxnTaVsoZIskm3eUZMv3mqiEnjPI9THV6Bs+VlVZGNJIvrZj1RVnAkCXFYvTqiVUGUm3r1Kq459jZgiLH/XZuqXBGZmjqbK2zIMBBNVi0riFIzlaxe4M88IS7Z1DgqMgGsbBO7PTP/Lo6JMtJwcsWuksgiM7Z6R0TxRz1stEhPm/INunBGEv/GSCj62/vttFSUvoty/DvKE7YAYFG2sA4TqVNL5BeizkH0DRRlw+GG4lWir/0XtIUIgSkbDlOilUzjNMMv8YUYa9Fd2TrCtZH4NYEQETBlT3qfG7GUHx8RzassEei1A2+EnxkIcXW0RsPief3enP0g8DxvlMnCsZlTC48sWikyDWtLMSm3K/TRkiO6RqZdFBW+IFAdOY7GYel6pGgiE1gik7MnjkPM0NPHY4n0MYyqrpDUm7Ho1moLoumITZOjohv2fDdb0udQf+jePsaURWdmBEysnwTUCFg0q7CKKqZmKPlWW5CeDYOKvyCaQtzqY7ND7ZgOK6enKyHEzDrnM9ITaFCpSENiDsqfJgU71FmlIs03WzVD1QzYmVvFjDf3rxxq4RtKGAPA+pHnVQTr5ydzSfiyb954/swP/9gjlnrCBRzYPKqdpQVKuueimru+7Zs3dl3e211g/uEQzJ8MMItLIc6B+VeUcjWOonFXGFErCk2s51EUnYdCi1r2e/Y/5JIVQn2w47EAAAAASUVORK5CYII="}],
    "CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],"MAX_DISPLAY":7,
    "SMOOTH":"false","AREA_STYLE":"false","STEP":"false"}))

# ═══ Line ═══
CHARTS.append(("06_Line_Basic", "line/basic.html", {
    "TITLE":"06 基础折线","CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "VALUES":[{"value": 6500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAilBMVEVHcEyZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWMnaiPn6qZqrVmdX9zgo2Wp7IpLzNwf4mAkJqMnah5iZN8jJeGlqGPoKtsfIaDk52JmaRpeIJ2hpCLm6UwNzs3PkNhbXRFTlRaZWx2hIyTo65vfIRodHySoq3+fuZKAAAAEnRSTlMAMJ+vYN8QQL+AIM+P71Bwv++BmxKZAAACeklEQVR4Xu3X15LbIBSAYUBUNScHyb1vT3n/14vbhj0WCNjkJjP5rz3fiINGBvLP9z/ZmkLDe0LXvCT50bqCYaKmeQwXEEq3uUyYSlyhLCDS1y/6EjNcjTgVRFuBq6oDay0g3mKO3IapoaMgpa4HnFapD4RbLwc2k8gpIane9gOpoWjnIa3jzsNztLK0dlsYl5pEaGE3Pom6EaVmdz5ISLf5iW2PXp/dIJMMdVvwpq5QnQ5ZP6SvkP5jCMpMaGsXfqi+QMIBzy8vzxDOuv3HiQvknNfpqdeR98hCIIqh6aWfIWgehiY+6CE8oi4EMQw9nZ2nkZWtQlCFobfH6fTxLbz5dg+hMAQP338EF7a39gDBqIMi9Qe3ssC0U99qa7+FoSIVWp6cOYQTDoo6hx5GKglJdOwexmoToM3s7KxgNBOFvi3tuRmMpyPQ/srYWR+BRPhPZLOYHw/2WtdDrMGHrV92XTezqBXEU/fQzt43W0A+VMH6nllDUgb/ixiA2UdltQFIhQy4hAKA9fzaegEZFQgqCHw2TRRaaPV3IO4mlhM7A0SiPeSQX6UuEEFQCflNblCFvuEiH5I3SCOIZTsFuUE1gtpsqH2HJgiSuU5D3iHlIEncyFJjt2Moegb1iSG11zNWhTaKnyCeu7JTknOJTuzsBNHclbkmjj+7eRAnLopPgzoLQndUgcZdDAHRBCF8M0YXAjOETPCSUBEUc1KRB2kMSe0kGoaoF8LVDuLB2wbxH4xw9DZj5vskyRtUeY5qw0putFG+n2v8xuHdH0kFL4lS+IYXDk+p4R8GgCVGIpWs+c0w9PTSOKpoSUJUcWO4op5ZqtaYiVIE9wvKcRFj0cNHIgAAAABJRU5ErkJggg=="}, {"value": 3500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEx0g46ZqrXM1t21w8uElJ/M1t2sucGZqrWZqrWZqrVmdX9od4HM1t2ZqrXM1t2ZqrXM1t3M1t1mdX+ZqrWZqrWwvsfM1t3M1t2ZqrWZqrXM1t3M1t2ZqrVndoBmdX9mdX/F0NjM1t1mdX+BkZyImKOvvcZ+jZiZqrXM1t1mdX/mqqqOn6qTo66GlqB+jpgpLzPVqq2Wp7JvfoinqrPIqq+0qrKdrrm7yNCntsBFTlTI0tpVYGe9qrA+RkthbXRsnZ8YAAAAKHRSTlMA/oCAMCOfEEC/n8Ng79+/YM8ghu+PSN9gz3CvUK/vr0p4j5+Iv9/PYy3u2QAAAuFJREFUeF6l1Glb4jAQwPFpaWmBgtwoKN67k/Ti9t79/t9qGxOY1aok6f99f89kQgDzvGbj/v7uKgDjBi3OW61B5Etoiu9lvyNTK5pzWSsSUHCGstQZGFL+gO8pX0gdfFtuN2Kq+RWYdcn3RfJwcRwvCypZ35pBYiSSQsRlXLRFXPFbY4ikLuI2VlLCB2ZHo+a+Kycq2iHmPAqLNKEWp3irgZtYtkRM+RqLbCC+EgPJNogOTyyhNWK8702cLdOHLknJUiRIrDvjuT4UKSZPUERHWxpCwfydWaFqRxDmJhBcEaNGIoiWrdNdihTS/RveWnCBn9odbm3NUUJe+/yYMx4ifi1tELmjoAk7OeK4+FWbbbzciceWSchjbPKz08SfyngqoRpjLADKC4wcdByUUK+ATskJ2jUjJ+WZhAJWNCPonE1MHMwdCcKYifoHqCbmo7pHnCRfKajGRHScG8batCUPdYM6E9G3JwVbB1XQ0YbEh6I6QbR8GKF2MGEy7wCRFKJ+wFQ9WvZeCjo2EKsRJLoJYIRWEBur35Fqco2WULsvII/kJ0uI9QIhtatD8u9kdoAebCD6NZ0y1SPaQCQFbTqZDURS3WYghJ4SaON9iw3RW6N6fTHSizxY+rpYLF5Tvdf/ufb5y97B54Xoj4YENVbuUTHoLGRcAxoTQKHqr4KeNaA+K/diA8Gk7DyixdFgVobo5g2WTU+i/FjV9T9rXT8t6Zs3lqFWANArHcwogq4/Ok9oCwWlBVlCUK/mEORVcwiCGe2nGtRX9/5g75zBe79oHMu6EsKHJ5qmwkCAFRt6FSE6mKqDqiRJqjhwoZg159wxpYZjODRF0YrLcrM9e0B5ciCuMpnJJYWWlGT5WkCZNtPw4WMj3JcVUKrLhPA5Hw+tEk2nWWLo3vTruD58WWh04TRMhZE6oxB+yh/qIM2uD8eaHrui0dgHrdzhd0TTDX0wKXRHjcaZ+rrIdadhqAn8A87BQoMTVo0lAAAAAElFTkSuQmCC"}, {"value": 3000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAnFBMVEVHcEyaqrWaqrSZqrWaqrSaqrWaqrWaqrWaqrSaqrSaqrSaqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrVibXQpLzN9jJZtfIaHlqBndX+Uo61wf4mAkJqXp7F6iZN0goyQoKqEk52aqrVqeIJ3hpCKmaONnaeXprBufYe5w8qLlp7Z4OT1+PrS19ucpq2xvsaltL3I0df7ApL7AAAAK3RSTlMAMEC//48QgHDvn8/fryDvcED/n2BQ/////////////////////////+/fbmjbTAAAAdJJREFUeAHt04WO6zAQheHjesI85c4yM77/u900V0VrFXsZ8okLv3JcF52v0ul0Op2O6ql3yWgi8vBafhD6/zsR1SK8VkyUNKWU5jReKyOiIA91QkRxUnhBEJRVpRZzqzLIdMoN3S9zvCj3UopogVcKXbApGeBFA1rDrdKhRceqxJ5Fx67Uh6lHNBqPR44lY11zecY1cisVPjblCRkhq1KAdSqOiIxpVqEUNT/W8bAXximZrEuq+VMY3EMl4NNkOntzKANCEpGdt4Y0ENGuyN5bQwxFtH9wePT2UEim/ePDjfQJtykYARmOpiJy7HYhGZnZOZWzHcdhlYY2dk1lRo4drirzOp7JAbmHYJzRuUz3nTusALU17FQu3DuMmqZ1BzJ5RSdFTV2uTZltDWM7GeauTs9XHTl6RYdL1NRM5LBJHR2IzF7T4Ry1Hl3fSN06nIpML17V0WhEt3f3D4d15cy8iHYqNILHu7u7J9rGTg/UCJ6er42M9lK2pLDQS2hTMvABP2ErfaxRYaajRcVTaOSF5U/Wqm/3QO0qtjBEu5wtVG5PpNO3hAa8BKhBkOl5L9E6GIIXBnA6bGxzOuzUJlSgHduE+DNDg8W21DzRKis23voHkmGCCGZlkZ0AAAAASUVORK5CYII="}, {"value": 2000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAjVBMVEVHcEwxNz0xNz0xNz0xNz2ZqrUxNz0xNz0xNz0xNz0xNz0xNz0xNz2ZqrWZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrUxNz2ZqrX///9FTVQ4PkWYm56To65LVFt/jZeMnKZyf4hlcXlseIFYYmpfaXJSW2OBJucVAAAAH3RSTlMA71DPr78ggBBA359ggEAwn78QcFCPYN+vj+8wIM9wM29S9wAAAdhJREFUeNrt1Ol22jAQhuGRF3nFxmxJun0GsjTpcv+X1xKJDoJjSbb8r3n+cYDXo7GBPnz4b6w2i/s0vV80FKRZ9md3u4BpHvpLy9XUztfetKRp0tN3NyuizfmA0073ue/TL6Ts9J5oit2nb/xCz9RQqIUKLShUGh7ik4WHmrQPDa2aZvNwpyuTli3rqgNee9MTbJKCrtUxTg79lTfYJbmRyWMoz9cDHeEQ52ZnIPQMp4RYhrOj2fkJDwUPJKCZy/5+gI/KHEg7Pv3L/IIfIXVHClw4vJwqLz9+w99ahSq8e9zvHzEelySU/V+YShJREhTihRdA+NFQ6oHCEWEe1M4VKuYK5Qgm1I4EQnUqVM0VknOFaItAmQ5RNleI8uJdtC0xRaRChqjDeIUOmYrxUxGHDJnAKPFQiGSMMbqB0Oj7mFlCox73yBaS8NfaQtTBG1lDtf+u7aEcvrb2ECXwFOlQ8NmkDoWerSQOuc5W0g0OVc7Qmu+LLRQ5Q/LiN3CjxFnuDPGHC8vzmuifZkbDKmi299bkVvNFb2R885nrAajpVsQX8RDzOq+1fBEPW8tFVUeQE88fWf5mMvLDj/XAtiX5SYa30OqBvM8WW/5Cy5x8xaKlAa0w3/sDh78rWpS3Kr8AAAAASUVORK5CYII="}, {"value": 1800, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEz/zE37tDT0kAz/zE3/zE12TCn+y0z0kAx1TCl1TCn/zE15Tih1TCn0kAz1kg7/zE30kAz+ykt1TCn/zE31kg7yjwz0kAz/zE11TCl1TCl1TCl4TSj1lBHyjgz3oB7/zE30kAx1TCn/zE3ywEmcZym6jDt1TCn/zE30kAz+x0f5pyT1lRD7szL8vDv3nRn9wUGNYC1/USbDdhf0w0vks0Wybx4rMTPcgxHNoUOtgjmDcj7qiw7OfBTkuEqZXyF8bTsrAAAAJ3RSTlMAvyBmYIDZQL8UgBBgQRDP30DvcDChgDCZpjC/79+PUM/vj69wv4DzeXUBAAADgElEQVR4XqWX63biOAyAHUigCeVOKXQo7XRmV5Jz49p7Z9//rRZr7DbjTkOIv1899JwPSZYtISzuYBGGLZgLVxYA3S4ACDHx/YmDCLRo4uGBmbPoGWUcSxzV1TRm+x0yWUKU4W1NT4DvpDklEoNams4MEXcvD7BjE6U46tTJyh/ggeeHh4cXJYozxJuTYwkGqHnRIsVPcSoevvPrIHpizX59d6pnggV2T7/YI5+hdaqojZ+JaQtwdWqd8RMp0SPAWJyIP0KLhIigztX18Q9WdOA/LpKbSSrRPUBYp6/bCn/wkdobwLmoTeeWRRkRvQLcifpMcqIklquYaA3fhAMXdCCX6t4BuIguSREj4hNA18V0zSaJuAOInHOjDBHX0HIRNbWIcwsdRA2TGu5VJzmgi825OU3KM338KO/dcrtIUvasEnNL3KaSTIg2TufmIxPzU+ISUvuPF6DlLCLFxqW7GwXRI7g8AcjkbNpu5q6ilJjX5bDnJuKQmBwHnncxnTaVsoZIskm3eUZMv3mqiEnjPI9THV6Bs+VlVZGNJIvrZj1RVnAkCXFYvTqiVUGUm3r1Kq459jZgiLH/XZuqXBGZmjqbK2zIMBBNVi0riFIzlaxe4M88IS7Z1DgqMgGsbBO7PTP/Lo6JMtJwcsWuksgiM7Z6R0TxRz1stEhPm/INunBGEv/GSCj62/vttFSUvoty/DvKE7YAYFG2sA4TqVNL5BeizkH0DRRlw+GG4lWir/0XtIUIgSkbDlOilUzjNMMv8YUYa9Fd2TrCtZH4NYEQETBlT3qfG7GUHx8RzassEei1A2+EnxkIcXW0RsPief3enP0g8DxvlMnCsZlTC48sWikyDWtLMSm3K/TRkiO6RqZdFBW+IFAdOY7GYel6pGgiE1gik7MnjkPM0NPHY4n0MYyqrpDUm7Ho1moLoumITZOjohv2fDdb0udQf+jePsaURWdmBEysnwTUCFg0q7CKKqZmKPlWW5CeDYOKvyCaQtzqY7ND7ZgOK6enKyHEzDrnM9ITaFCpSENiDsqfJgU71FmlIs03WzVD1QzYmVvFjDf3rxxq4RtKGAPA+pHnVQTr5ydzSfiyb954/swP/9gjlnrCBRzYPKqdpQVKuueimru+7Zs3dl3e211g/uEQzJ8MMItLIc6B+VeUcjWOonFXGFErCk2s51EUnYdCi1r2e/Y/5JIVQn2w47EAAAAASUVORK5CYII="}],
    "SMOOTH":"false","AREA_STYLE":"false","STEP":"false"}))

CHARTS.append(("07_Line_Stacked", "line/stack.html", {
    "TITLE":"07 堆叠折线","CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "SERIES":D([{"name":"Email","type":"line","stack":"x","areaStyle":{},"data":[120,132,101,134,90,230]},
                {"name":"Union Ads","type":"line","stack":"x","areaStyle":{},"data":[220,182,191,234,290,330]},
                {"name":"Video Ads","type":"line","stack":"x","areaStyle":{},"data":[150,232,201,154,190,330]}]),
    "SMOOTH":"false"}))

CHARTS.append(("08_Line_XY", "line/xy.html", {
    "TITLE":"08 XY折线","SMOOTH":"false",
    "DATA":D([[4,4.26],[5,5.68],[6,7.24],[7,4.82],[8,6.95],[9,8.81],[10,8.04],[11,8.33],[12,10.84],[13,7.58],[14,9.96]])}))

# ═══ Pie ═══
CHARTS.append(("09_Pie_Basic", "pie/basic.html", {
    "TITLE":"09 基础饼图","ROSE_TYPE":"false","LABEL_SHOW":"true","RADIUS":D(["40%","70%"]),
    "DATA":D([{"name":"搜索","value":1048},{"name":"直接","value":735},{"name":"邮件","value":580},{"name":"联盟","value":484},{"name":"视频","value":300}])}))

CHARTS.append(("38_Pie_Rose", "pie/basic.html", {
    "TITLE":"38 玫瑰图","ROSE_TYPE":"area","LABEL_SHOW":"true","RADIUS":D(["20%","80%"]),
    "DATA":D([{"name":"A","value":40},{"name":"B","value":38},{"name":"C","value":32},{"name":"D","value":30},{"name":"E","value":28},{"name":"F","value":26},{"name":"G","value":22},{"name":"H","value":18}])}))

# ═══ Scatter ═══
CHARTS.append(("10_Scatter_Basic", "scatter/basic.html", {
    "TITLE":"10 基础散点","SYMBOL_SIZE":10,
    "DATA":D([[10,8.04],[8,6.95],[13,7.58],[9,8.81],[11,8.33],[14,9.96],[6,7.24],[4,4.26],[12,10.84],[7,4.82],[5,5.68]])}))

CHARTS.append(("11_Scatter_Bubble", "scatter/bubble.html", {
    "TITLE":"11 气泡散点","X_NAME":"GDP","Y_NAME":"Life Expectancy","VMIN":0,"VMAX":100,
    "DATA":D([[28604,77,80],[31163,77.4,90],[1516,68,15],[13670,74.7,40],[28599,75,60],[29476,77.1,70],[31476,75.4,85],[28666,78.1,50],[12124,72.6,25],[11173,72.8,100]]),
    "SMOOTH":"false","AREA_STYLE":"false","STEP":"false"}))

CHARTS.append(("12_Scatter_Geo", "scatter/geo.html", {
    "TITLE":"12 地理散点","MAP_NAME":"china","VMIN":0,"VMAX":100,"SIZE_SCALE":"5",
    "GEO_COORD_MAP":D({"北京":[116.46,39.92],"上海":[121.48,31.22],"广州":[113.23,23.16],"深圳":[114.07,22.62],"成都":[104.06,30.67]}),
    "DATA":D([{"name":"北京","value":100},{"name":"上海","value":95},{"name":"广州","value":80},{"name":"深圳","value":90},{"name":"成都","value":70}])}))

CHARTS.append(("30_EffectScatter", "effectScatter/basic.html", {
    "TITLE":"30 涟漪散点","SIZE_SCALE":"1","MAP_NAME":"china",
    "GEO_COORD_MAP":D({"北京":[116.46,39.92],"上海":[121.48,31.22],"广州":[113.23,23.16],"深圳":[114.07,22.62],"成都":[104.06,30.67]}),
    "DATA":D([{"name":"北京","value":100,"itemStyle":{"color":"#dd6b66"}},{"name":"上海","value":95,"itemStyle":{"color":"#759aa0"}},{"name":"广州","value":80,"itemStyle":{"color":"#e69d87"}},{"name":"深圳","value":90,"itemStyle":{"color":"#8dc1a9"}},{"name":"成都","value":70,"itemStyle":{"color":"#ea7e53"}}])}))

# ═══ Map ═══
CHARTS.append(("13_Map_China", "map/basic.html", {
    "TITLE":"13 中国地图","MAP_NAME":"china","VMIN":98,"VMAX":38072,"LABEL_SHOW":"false",
    "DATA":D([{"name":"广东","value":38072},{"name":"北京","value":26593},{"name":"上海","value":21073},{"name":"江苏","value":18296},{"name":"浙江","value":16976},{"name":"山东","value":14386},{"name":"四川","value":12852},{"name":"福建","value":12359},{"name":"湖北","value":10388}])}))

# ═══ Radar ═══
CHARTS.append(("14_Radar_Basic", "radar/basic.html", {
    "TITLE":"14 雷达图","LEGEND_NAMES":D(["预算","实际"]),"SHAPE":"polygon",
    "INDICATORS":D([{"name":"预算","max":5000},{"name":"支出","max":15000},{"name":"销售","max":30000},{"name":"利润","max":40000}]),
    "DATA":D([{"name":"预算","value":[4200,3000,20000,35000]},{"name":"实际","value":[5000,14000,28000,26000]}])}))

# ═══ Gauge ═══
CHARTS.append(("15_Gauge", "gauge/basic.html", {
    "TITLE":"15 仪表盘","VALUE":78.5,"NAME":"完成率","UNIT":"%","MIN":0,"MAX":100,
    "START_ANGLE":225,"END_ANGLE":-45,"AXIS_WIDTH":30,"LABEL_SHOW":"true","PROGRESS_SHOW":"false"}))

# ═══ Funnel ═══
CHARTS.append(("16_Funnel", "funnel/basic.html", {
    "TITLE":"16 漏斗图","SORT":"descending","MAX_VALUE":10000,"MIN_VALUE":1800,"LABEL_POS":"inside",
    "DATA":D([{"name":"访问","value":10000},{"name":"注册","value":6500},{"name":"激活","value":4200},{"name":"下单","value":2800},{"name":"支付","value":1800}])}))

# ═══ Heatmap ═══
CHARTS.append(("17_Heatmap", "heatmap/basic.html", {
    "TITLE":"17 热力图","LABEL_SHOW":"false","VMIN":0,"VMAX":30,
    "X_LABELS":D(["Mon","Tue","Wed","Thu","Fri"]),
    "Y_LABELS":D(["0h","2h","4h","6h","8h","10h","12h","14h","16h","18h","20h","22h"]),
    "DATA":D([[0,0,5],[0,1,10],[0,2,8],[0,3,7],[0,4,12],[0,5,15],[0,6,10],[0,7,8],[0,8,5],[0,9,12],[0,10,18],[0,11,15]])}))

# ═══ Candlestick ═══
CHARTS.append(("18_Candlestick", "candlestick/basic.html", {
    "TITLE":"18 K线图","DATES":D(["1日","2日","3日","4日","5日","6日","7日"]),
    "DATA":D([[20,34,10,38],[40,35,30,50],[31,38,33,44],[38,15,5,42],[11,35,8,35],[29,43,20,49],[41,26,18,42]])}))

# ═══ Treemap ═══
CHARTS.append(("19_Treemap", "treemap/basic.html", {
    "TITLE":"19 矩形树图","NODE_CLICK":"false","UPPER_LABEL_SHOW":"true","BREADCRUMB_SHOW":"true",
    "DATA":D([{"name":"电子产品","value":20000,"children":[
        {"name":"手机","value":8000},{"name":"电脑","value":6000},{"name":"平板","value":4000},{"name":"耳机","value":2000}]},
      {"name":"家居用品","value":12000,"children":[
        {"name":"家具","value":5000},{"name":"灯具","value":3000},{"name":"厨具","value":2500},{"name":"园艺","value":1500}]},
      {"name":"服装鞋帽","value":8000,"children":[
        {"name":"男装","value":3500},{"name":"女装","value":3000},{"name":"童装","value":1500}]}])}))

# ═══ Sunburst ═══
CHARTS.append(("20_Sunburst", "sunburst/basic.html", {
    "TITLE":"20 旭日图","LABEL_SHOW":"true","NODE_CLICK":"false","FOCUS":"ancestor","RADIUS":D(["0%","90%"]),"ROTATE":0,
    "DATA":D([{"name":"A","itemStyle":{"color":"#5470c6"},"children":[{"name":"A1","value":25},{"name":"A2","value":15}]},
              {"name":"B","itemStyle":{"color":"#91cc75"},"children":[{"name":"B1","value":20},{"name":"B2","value":10}]}])}))

# ═══ Sankey ═══
CHARTS.append(("21_Sankey", "sankey/basic.html", {
    "TITLE":"21 桑基图","NODE_ALIGN":"left","LABEL_POS":"right","ORIENT":"horizontal",
    "NODES":D([{"name":"首页"},{"name":"搜索"},{"name":"详情"},{"name":"下单"}]),
    "LINKS":D([{"source":"首页","target":"搜索","value":40},{"source":"首页","target":"详情","value":20},{"source":"搜索","target":"详情","value":25},{"source":"详情","target":"下单","value":35}])}))

# ═══ Graph ═══
CHARTS.append(("22_Graph_Force", "graph/force.html", {
    "TITLE":"22 力导向图","LAYOUT":"force","REPULSION":50,"EDGE_LENGTH":100,"GRAVITY":0.1,
    "LAYOUT_ANIMATION":"true","LABEL_SHOW":"true","SYMBOL_SIZE":30,"LEGEND":"false",
    "NODES":D([{"name":"A","category":0},{"name":"B","category":0},{"name":"C","category":1},{"name":"D","category":1},{"name":"E","category":2}]),
    "LINKS":D([{"source":"A","target":"B"},{"source":"A","target":"C"},{"source":"B","target":"D"},{"source":"C","target":"D"},{"source":"C","target":"E"}]),
    "CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"]}))

# ═══ Tree ═══
CHARTS.append(("23_Tree", "tree/basic.html", {
    "TITLE":"23 树图","LAYOUT":"orthogonal","ORIENT":"LR","LABEL_POS":"right","EXPAND_COLLAPSE":"true","LEAF_POS":"none",
    "DATA":D([{"name": "CEO", "children": [{"name": "CTO", "children": [{"name": "工程师A"}, {"name": "工程师B"}]}, {"name": "CFO", "children": [{"name": "会计A"}]}]}])}))

# ═══ Boxplot ═══
CHARTS.append(("24_Boxplot", "boxplot/basic.html", {
    "TITLE":"24 箱线图","Y_AXIS_NAME":"","CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "DATA":D([[740,880,935,980,1070],[800,860,900,940,960]])}))

# ═══ Parallel ═══
CHARTS.append(("25_Parallel", "parallel/basic.html", {
    "TITLE":"25 平行坐标",
    "DATA":D([[55,85,78,90,65,"A"],[70,80,82,95,72,"B"],[60,75,68,85,58,"C"],[80,90,88,92,78,"D"],[45,65,55,70,48,"E"]]),
    "PARALLEL_AXIS":D([{"dim":0,"name":"A"},{"dim":1,"name":"B"},{"dim":2,"name":"C"},{"dim":3,"name":"D"},{"dim":4,"name":"E"}])}))

# ═══ Calendar ═══
CHARTS.append(("26_Calendar", "calendar/heatmap.html", {
    "TITLE":"26 日历热力","RANGE_START":"2024-01-01","RANGE_END":"2024-12-31","VMIN":0,"VMAX":250,"ORIENT":"horizontal",
    "DATA":D([["2024-01-05",120],["2024-02-03",200],["2024-03-10",90],["2024-04-07",220],["2024-05-05",160],["2024-06-12",130]])}))

# ═══ ThemeRiver ═══
CHARTS.append(("27_ThemeRiver", "themeRiver/basic.html", {
    "TITLE":"27 主题河流","LEGEND":"true",
    "DATA":D([["2015/11/08",10,"Evolution"],["2015/11/09",15,"Evolution"],["2015/11/08",10,"Natural"],["2015/11/09",15,"Natural"],["2015/11/08",10,"Deep"],["2015/11/09",20,"Deep"]])}))

# ═══ PictorialBar ═══
CHARTS.append(("28_PictorialBar", "pictorialBar/basic.html", {
    "TITLE":"28 象形柱图","SYMBOL":"","SYMBOL_SIZE":[40,40],"SYMBOL_MARGIN":"5%","SYMBOL_CLIP":"false",
    "SYMBOL_BOUNDING":1000,"SYMBOL_REPEAT":"true","SYMBOL_POS":"start","COLOR":"#5470c6","LABEL_SHOW":"true",
    "CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "VALUES":[{"value": 6500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAilBMVEVHcEyZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWMnaiPn6qZqrVmdX9zgo2Wp7IpLzNwf4mAkJqMnah5iZN8jJeGlqGPoKtsfIaDk52JmaRpeIJ2hpCLm6UwNzs3PkNhbXRFTlRaZWx2hIyTo65vfIRodHySoq3+fuZKAAAAEnRSTlMAMJ+vYN8QQL+AIM+P71Bwv++BmxKZAAACeklEQVR4Xu3X15LbIBSAYUBUNScHyb1vT3n/14vbhj0WCNjkJjP5rz3fiINGBvLP9z/ZmkLDe0LXvCT50bqCYaKmeQwXEEq3uUyYSlyhLCDS1y/6EjNcjTgVRFuBq6oDay0g3mKO3IapoaMgpa4HnFapD4RbLwc2k8gpIane9gOpoWjnIa3jzsNztLK0dlsYl5pEaGE3Pom6EaVmdz5ISLf5iW2PXp/dIJMMdVvwpq5QnQ5ZP6SvkP5jCMpMaGsXfqi+QMIBzy8vzxDOuv3HiQvknNfpqdeR98hCIIqh6aWfIWgehiY+6CE8oi4EMQw9nZ2nkZWtQlCFobfH6fTxLbz5dg+hMAQP338EF7a39gDBqIMi9Qe3ssC0U99qa7+FoSIVWp6cOYQTDoo6hx5GKglJdOwexmoToM3s7KxgNBOFvi3tuRmMpyPQ/srYWR+BRPhPZLOYHw/2WtdDrMGHrV92XTezqBXEU/fQzt43W0A+VMH6nllDUgb/ixiA2UdltQFIhQy4hAKA9fzaegEZFQgqCHw2TRRaaPV3IO4mlhM7A0SiPeSQX6UuEEFQCflNblCFvuEiH5I3SCOIZTsFuUE1gtpsqH2HJgiSuU5D3iHlIEncyFJjt2Moegb1iSG11zNWhTaKnyCeu7JTknOJTuzsBNHclbkmjj+7eRAnLopPgzoLQndUgcZdDAHRBCF8M0YXAjOETPCSUBEUc1KRB2kMSe0kGoaoF8LVDuLB2wbxH4xw9DZj5vskyRtUeY5qw0putFG+n2v8xuHdH0kFL4lS+IYXDk+p4R8GgCVGIpWs+c0w9PTSOKpoSUJUcWO4op5ZqtaYiVIE9wvKcRFj0cNHIgAAAABJRU5ErkJggg=="}, {"value": 3500, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEx0g46ZqrXM1t21w8uElJ/M1t2sucGZqrWZqrWZqrVmdX9od4HM1t2ZqrXM1t2ZqrXM1t3M1t1mdX+ZqrWZqrWwvsfM1t3M1t2ZqrWZqrXM1t3M1t2ZqrVndoBmdX9mdX/F0NjM1t1mdX+BkZyImKOvvcZ+jZiZqrXM1t1mdX/mqqqOn6qTo66GlqB+jpgpLzPVqq2Wp7JvfoinqrPIqq+0qrKdrrm7yNCntsBFTlTI0tpVYGe9qrA+RkthbXRsnZ8YAAAAKHRSTlMA/oCAMCOfEEC/n8Ng79+/YM8ghu+PSN9gz3CvUK/vr0p4j5+Iv9/PYy3u2QAAAuFJREFUeF6l1Glb4jAQwPFpaWmBgtwoKN67k/Ti9t79/t9qGxOY1aok6f99f89kQgDzvGbj/v7uKgDjBi3OW61B5Etoiu9lvyNTK5pzWSsSUHCGstQZGFL+gO8pX0gdfFtuN2Kq+RWYdcn3RfJwcRwvCypZ35pBYiSSQsRlXLRFXPFbY4ikLuI2VlLCB2ZHo+a+Kycq2iHmPAqLNKEWp3irgZtYtkRM+RqLbCC+EgPJNogOTyyhNWK8702cLdOHLknJUiRIrDvjuT4UKSZPUERHWxpCwfydWaFqRxDmJhBcEaNGIoiWrdNdihTS/RveWnCBn9odbm3NUUJe+/yYMx4ifi1tELmjoAk7OeK4+FWbbbzciceWSchjbPKz08SfyngqoRpjLADKC4wcdByUUK+ATskJ2jUjJ+WZhAJWNCPonE1MHMwdCcKYifoHqCbmo7pHnCRfKajGRHScG8batCUPdYM6E9G3JwVbB1XQ0YbEh6I6QbR8GKF2MGEy7wCRFKJ+wFQ9WvZeCjo2EKsRJLoJYIRWEBur35Fqco2WULsvII/kJ0uI9QIhtatD8u9kdoAebCD6NZ0y1SPaQCQFbTqZDURS3WYghJ4SaON9iw3RW6N6fTHSizxY+rpYLF5Tvdf/ufb5y97B54Xoj4YENVbuUTHoLGRcAxoTQKHqr4KeNaA+K/diA8Gk7DyixdFgVobo5g2WTU+i/FjV9T9rXT8t6Zs3lqFWANArHcwogq4/Ok9oCwWlBVlCUK/mEORVcwiCGe2nGtRX9/5g75zBe79oHMu6EsKHJ5qmwkCAFRt6FSE6mKqDqiRJqjhwoZg159wxpYZjODRF0YrLcrM9e0B5ciCuMpnJJYWWlGT5WkCZNtPw4WMj3JcVUKrLhPA5Hw+tEk2nWWLo3vTruD58WWh04TRMhZE6oxB+yh/qIM2uD8eaHrui0dgHrdzhd0TTDX0wKXRHjcaZ+rrIdadhqAn8A87BQoMTVo0lAAAAAElFTkSuQmCC"}, {"value": 3000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAnFBMVEVHcEyaqrWaqrSZqrWaqrSaqrWaqrWaqrWaqrSaqrSaqrSaqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrVibXQpLzN9jJZtfIaHlqBndX+Uo61wf4mAkJqXp7F6iZN0goyQoKqEk52aqrVqeIJ3hpCKmaONnaeXprBufYe5w8qLlp7Z4OT1+PrS19ucpq2xvsaltL3I0df7ApL7AAAAK3RSTlMAMEC//48QgHDvn8/fryDvcED/n2BQ/////////////////////////+/fbmjbTAAAAdJJREFUeAHt04WO6zAQheHjesI85c4yM77/u900V0VrFXsZ8okLv3JcF52v0ul0Op2O6ql3yWgi8vBafhD6/zsR1SK8VkyUNKWU5jReKyOiIA91QkRxUnhBEJRVpRZzqzLIdMoN3S9zvCj3UopogVcKXbApGeBFA1rDrdKhRceqxJ5Fx67Uh6lHNBqPR44lY11zecY1cisVPjblCRkhq1KAdSqOiIxpVqEUNT/W8bAXximZrEuq+VMY3EMl4NNkOntzKANCEpGdt4Y0ENGuyN5bQwxFtH9wePT2UEim/ePDjfQJtykYARmOpiJy7HYhGZnZOZWzHcdhlYY2dk1lRo4drirzOp7JAbmHYJzRuUz3nTusALU17FQu3DuMmqZ1BzJ5RSdFTV2uTZltDWM7GeauTs9XHTl6RYdL1NRM5LBJHR2IzF7T4Ry1Hl3fSN06nIpML17V0WhEt3f3D4d15cy8iHYqNILHu7u7J9rGTg/UCJ6er42M9lK2pLDQS2hTMvABP2ErfaxRYaajRcVTaOSF5U/Wqm/3QO0qtjBEu5wtVG5PpNO3hAa8BKhBkOl5L9E6GIIXBnA6bGxzOuzUJlSgHduE+DNDg8W21DzRKis23voHkmGCCGZlkZ0AAAAASUVORK5CYII="}, {"value": 2000, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAjVBMVEVHcEwxNz0xNz0xNz0xNz2ZqrUxNz0xNz0xNz0xNz0xNz0xNz0xNz2ZqrWZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrUxNz2ZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrWZqrUxNz2ZqrX///9FTVQ4PkWYm56To65LVFt/jZeMnKZyf4hlcXlseIFYYmpfaXJSW2OBJucVAAAAH3RSTlMA71DPr78ggBBA359ggEAwn78QcFCPYN+vj+8wIM9wM29S9wAAAdhJREFUeNrt1Ol22jAQhuGRF3nFxmxJun0GsjTpcv+X1xKJDoJjSbb8r3n+cYDXo7GBPnz4b6w2i/s0vV80FKRZ9md3u4BpHvpLy9XUztfetKRp0tN3NyuizfmA0073ue/TL6Ts9J5oit2nb/xCz9RQqIUKLShUGh7ik4WHmrQPDa2aZvNwpyuTli3rqgNee9MTbJKCrtUxTg79lTfYJbmRyWMoz9cDHeEQ52ZnIPQMp4RYhrOj2fkJDwUPJKCZy/5+gI/KHEg7Pv3L/IIfIXVHClw4vJwqLz9+w99ahSq8e9zvHzEelySU/V+YShJREhTihRdA+NFQ6oHCEWEe1M4VKuYK5Qgm1I4EQnUqVM0VknOFaItAmQ5RNleI8uJdtC0xRaRChqjDeIUOmYrxUxGHDJnAKPFQiGSMMbqB0Oj7mFlCox73yBaS8NfaQtTBG1lDtf+u7aEcvrb2ECXwFOlQ8NmkDoWerSQOuc5W0g0OVc7Qmu+LLRQ5Q/LiN3CjxFnuDPGHC8vzmuifZkbDKmi299bkVvNFb2R885nrAajpVsQX8RDzOq+1fBEPW8tFVUeQE88fWf5mMvLDj/XAtiX5SYa30OqBvM8WW/5Cy5x8xaKlAa0w3/sDh78rWpS3Kr8AAAAASUVORK5CYII="}, {"value": 1800, "symbol": "image://data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEz/zE37tDT0kAz/zE3/zE12TCn+y0z0kAx1TCl1TCn/zE15Tih1TCn0kAz1kg7/zE30kAz+ykt1TCn/zE31kg7yjwz0kAz/zE11TCl1TCl1TCl4TSj1lBHyjgz3oB7/zE30kAx1TCn/zE3ywEmcZym6jDt1TCn/zE30kAz+x0f5pyT1lRD7szL8vDv3nRn9wUGNYC1/USbDdhf0w0vks0Wybx4rMTPcgxHNoUOtgjmDcj7qiw7OfBTkuEqZXyF8bTsrAAAAJ3RSTlMAvyBmYIDZQL8UgBBgQRDP30DvcDChgDCZpjC/79+PUM/vj69wv4DzeXUBAAADgElEQVR4XqWX63biOAyAHUigCeVOKXQo7XRmV5Jz49p7Z9//rRZr7DbjTkOIv1899JwPSZYtISzuYBGGLZgLVxYA3S4ACDHx/YmDCLRo4uGBmbPoGWUcSxzV1TRm+x0yWUKU4W1NT4DvpDklEoNams4MEXcvD7BjE6U46tTJyh/ggeeHh4cXJYozxJuTYwkGqHnRIsVPcSoevvPrIHpizX59d6pnggV2T7/YI5+hdaqojZ+JaQtwdWqd8RMp0SPAWJyIP0KLhIigztX18Q9WdOA/LpKbSSrRPUBYp6/bCn/wkdobwLmoTeeWRRkRvQLcifpMcqIklquYaA3fhAMXdCCX6t4BuIguSREj4hNA18V0zSaJuAOInHOjDBHX0HIRNbWIcwsdRA2TGu5VJzmgi825OU3KM338KO/dcrtIUvasEnNL3KaSTIg2TufmIxPzU+ISUvuPF6DlLCLFxqW7GwXRI7g8AcjkbNpu5q6ilJjX5bDnJuKQmBwHnncxnTaVsoZIskm3eUZMv3mqiEnjPI9THV6Bs+VlVZGNJIvrZj1RVnAkCXFYvTqiVUGUm3r1Kq459jZgiLH/XZuqXBGZmjqbK2zIMBBNVi0riFIzlaxe4M88IS7Z1DgqMgGsbBO7PTP/Lo6JMtJwcsWuksgiM7Z6R0TxRz1stEhPm/INunBGEv/GSCj62/vttFSUvoty/DvKE7YAYFG2sA4TqVNL5BeizkH0DRRlw+GG4lWir/0XtIUIgSkbDlOilUzjNMMv8YUYa9Fd2TrCtZH4NYEQETBlT3qfG7GUHx8RzassEei1A2+EnxkIcXW0RsPief3enP0g8DxvlMnCsZlTC48sWikyDWtLMSm3K/TRkiO6RqZdFBW+IFAdOY7GYel6pGgiE1gik7MnjkPM0NPHY4n0MYyqrpDUm7Ho1moLoumITZOjohv2fDdb0udQf+jePsaURWdmBEysnwTUCFg0q7CKKqZmKPlWW5CeDYOKvyCaQtzqY7ND7ZgOK6enKyHEzDrnM9ITaFCpSENiDsqfJgU71FmlIs03WzVD1QzYmVvFjDf3rxxq4RtKGAPA+pHnVQTr5ydzSfiyb954/swP/9gjlnrCBRzYPKqdpQVKuueimru+7Zs3dl3e211g/uEQzJ8MMItLIc6B+VeUcjWOonFXGFErCk2s51EUnYdCi1r2e/Y/5JIVQn2w47EAAAAASUVORK5CYII="}]}))

# ═══ Chord ═══
CHARTS.append(("29_Chord", "chord/basic.html", {
    "TITLE":"29 和弦图","LABEL_ROTATE":"false",
    "NODES":D([{"name":"北京"},{"name":"上海"},{"name":"广州"},{"name":"深圳"},{"name":"成都"}]),
    "LINKS":D([{"source":"北京","target":"上海","value":95},{"source":"北京","target":"广州","value":60},{"source":"上海","target":"深圳","value":55},{"source":"广州","target":"深圳","value":70}])}))

# ═══ Lines (flights) ═══
CHARTS.append(("31_Lines_Flights", "lines/flights.html", {
    "TITLE":"31 航班线路","MAP_NAME":"china","LINE_SCALE":"1",
    "GEO_COORD_MAP":D({"北京":[116.46,39.92],"上海":[121.48,31.22],"广州":[113.23,23.16],"深圳":[114.07,22.62]}),
    "FLIGHTS":D([["北京","上海",100],["北京","广州",80],["上海","深圳",90]])}))

# ═══ Mix ═══
CHARTS.append(("32_Mix_Line_Bar", "mix/line-bar.html", {
    "TITLE":"32 混合图表","LINE_NAME":"折线","BAR_NAME":"柱状",
    "CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "BAR_DATA":D([320,332,301,334,390,330]),
    "LINE_DATA":D([220,182,191,234,290,310])}))

CHARTS.append(("41_Mix_Timeline", "mix/timeline.html", {
    "OPTIONS":"[]",
    "TITLE":"41 时间轴",
    "TIMELINE":D([2020,2021,2022]),
    "CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "SERIES":D([{"name":"A","type":"bar","data":[120,145,170]},{"name":"B","type":"bar","data":[90,110,130]},{"name":"C","type":"bar","data":[70,85,100]}])}))

# ═══ 3D ═══
CHARTS.append(("33_3D_Bar", "3d/bar3d.html", {
    "DATA":D([["A","Q1",120],["A","Q2",200],["B","Q1",90],["B","Q2",130],["C","Q1",160],["C","Q2",220]]),
    "TITLE":"33 3D柱状","GL_INLINE":"","VMAX":250,"COORD_SYSTEM":"cartesian3D","BAR_SIZE":0.3,
    "AXIS_3D":D([{"name":"X","data":["A","B","C"]},{"name":"Y","data":["Q1","Q2","Q3","Q4"]},{"name":"Z"}])}))

CHARTS.append(("34_3D_Scatter", "3d/scatter3d.html", {
    "DATA":D([[10,20,30],[20,10,40],[30,30,20],[15,25,35],[25,15,25]]),
    "TITLE":"34 3D散点","GL_INLINE":"","SYMBOL_SIZE":10,
    "AXIS_3D":D([{"name":"X"},{"name":"Y"},{"name":"Z"}])}))

CHARTS.append(("35_3D_Surface", "3d/surface.html", {
    "TITLE":"35 3D曲面","GL_INLINE":"","PROJECTION":"perspective","WIREFRAME":"false","COLOR":"#5470c6",
    "DATA_OR_EQUATION":"function(x,y){return Math.sin(x)*Math.cos(y)}","PARAMETRIC":"false"}))

CHARTS.append(("36_3D_Globe", "3d/globe.html", {
    "TITLE":"36 3D地球","GL_INLINE":"","AUTO_ROTATE":"true","SHADING":"lambert","ENVIRONMENT":"","BASE_TEXTURE":"","HEIGHT_TEXTURE":"",
    "SCATTER_SERIES":"[]","LAYERS":"[]"}))

CHARTS.append(("37_3D_Lines3D", "3d/lines3d.html", {
    "GEO_COORD_MAP":"{}",
    "TITLE":"37 3D折线","GL_INLINE":"","AUTO_ROTATE":"false","ENVIRONMENT":"","BASE_TEXTURE":"","LINE_COLOR":"#ff6600",
    "FLIGHTS":D([{"fromName":"A","toName":"B","coords":[[0,0,0],[10,10,10]]},
                 {"fromName":"B","toName":"C","coords":[[10,10,10],[20,20,30]]}])}))

# ═══ Misc ═══
CHARTS.append(("39_Custom_Error_Bar", "custom/error-bar.html", {
    "TITLE":"39 误差柱图","RENDER_ITEM":"false","ENCODE":"{}",
    "CATEGORIES":["大象", "犀牛", "河马", "水牛", "长颈鹿"],
    "DATA":D([[50,45,55],[65,60,72],[55,50,62],[70,65,80],[60,55,68]])}))

CHARTS.append(("40_Geo_Lines", "geo/lines.html", {
    "TITLE":"40 全国线路","MAP_NAME":"china","SIZE_SCALE":"1","EFFECT_DATA":"[]",
    "GEO_COORD_MAP":D({"北京":[116.46,39.92],"上海":[121.48,31.22],"广州":[113.23,23.16]}),
    "FLIGHTS":D([["北京","上海",100],["上海","广州",80]])}))

# ═════════════════════════════════════════════════════════
# Validate & Generate
# ═════════════════════════════════════════════════════════
results = []
for name, tpl_rel, data in CHARTS:
    tpl_path = os.path.join(TPL, tpl_rel)
    if not os.path.exists(tpl_path):
        results.append(("⏭️", name, f"missing: {tpl_rel}"))
        continue
    # Check placeholder coverage
    with open(tpl_path) as f:
        tpl_content = f.read()
    needed = set(re.findall(r'\{\{(\w+)\}\}', tpl_content)) - {'ECHARTS_INLINE','MAP_INLINE','GL_INLINE'}
    missing = needed - set(data.keys())
    if missing:
        results.append(("❌", name, f"missing keys: {missing}"))
        continue
    try:
        out = os.path.join(OUT, f"{name}.html")
        build(tpl_path, data, out)
        # Verify no unresolved placeholders remain
        with open(out) as f:
            out_content = f.read()
        remaining = re.findall(r'\{\{(\w+)\}\}', out_content)
        if remaining:
            results.append(("❌", name, f"unresolved: {remaining}"))
        else:
            results.append(("✅", name, f"{os.path.getsize(out)} bytes"))
    except Exception as e:
        results.append(("❌", name, str(e)[:120]))

ok = sum(1 for r in results if r[0]=="✅")
sk = sum(1 for r in results if r[0]=="⏭️")
bad = sum(1 for r in results if r[0]=="❌")
print(f"\n{'='*60}")
print(f"  Results: {ok} passed, {bad} failed, {sk} skipped ({len(results)} total)")
print(f"{'='*60}")
for s,n,d in results:
    if s != "✅": print(f"  {s} {n:<30s} {d}")
with open(f"{OUT}/_summary.json","w") as f:
    json.dump([{"status":s,"name":n,"detail":d} for s,n,d in results], f, ensure_ascii=False, indent=2)
print(f"\nOutput: {OUT}")
