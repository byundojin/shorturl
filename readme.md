# URL Short

긴 URL을 짧은 URL로 변환하여 주는 서비스입니다.

## 실행

docker-compose를 통해 실행 할 수 있습니다.

```
docker-compose -p <project 이름> up
```

## 설명

URL Short의 핵심 기능은 다음과 같습니다.

- 짧은 URL 생성
- 원본 URL로 이동
- URL 조회수 확인

### 짧은 URL 생성

원본 URL로 이동할 수 있는 짧은 URL을 생성합니다.<br>
만료 기간을 지정하여 URL의 이용 기간을 정할 수 있습니다.

#### 요청

`POST - /shorten`

```
{
    "url": <원본 url>,
    "exp_date": <url 만료 기간> # ISO 8601 표기법을 사용해야 합니다.
}                              # ex) 년도-월-일T시간:분:초
                               #     2024-07-08T15:58:01
```

#### 응답

`201 - Created` 성공적으로 생성됨

```
{
    "short_url" : <짧은 url>
}
```

`400 - BadRequest` exp_date를 ISO 8601 표기법으로 보내지 않음

```
{
"detail":"exp_date가 ISO 8601 표기법을 따르지 않음"
}
```

`410 - Gone` exp_date가 만료됨

```
{
    "detail":"기간 만료"
}
```

`503 Service Unavailable` Redis가 연결되지 않음

```
{
    "detail":"redis 연결 불가"
}
```

### 원본 URL로 이동

짧은 URL을 사용해 원본 URL로 redirect됩니다.

#### 요청

`GET - /<짧은 url>`

#### 응답

`301 Multiple Choice` 원본 url로 redirect됨

```
redirect -> <원본 url>
```

`404 - Not Found` url을 찾을 수 없음

```
{
    "detail":"url을 찾을 수 없음"
}
```

`410 - Gone` exp_date가 만료됨

```
{
    "detail":"기간 만료"
}
```

`503 Service Unavailable` Redis가 연결되지 않음

```
{
    "detail":"redis 연결 불가"
}
```

### URL 조회수 확인

원본 URL로 redirect된 횟수를 확인합니다.

#### 요청

`GET - /stat/<짧은 url>`

#### 응답

`200 - OK` 성공적인 응답

```
{
    "views": <조회수>
}
```

`404 - Not Found` url을 찾을 수 없음

```
{
    "detail":"url을 찾을 수 없음"
}
```

`410 - Gone` exp_date가 만료됨

```
{
    "detail":"기간 만료"
}
```

`503 Service Unavailable` Redis가 연결되지 않음

```
{
    "detail":"redis 연결 불가"
}
```

---

# Redis 사용 이유

Redis를 사용한 이유는 다음과 같습니다.

- NoSQL
- 수평 확장 용이
- 빠른 속도

### NoSQL

기존의 형식이 아닌 Key:Value형식의 Redis를 선택한 이유는 다음과 같습니다.

- 모든 데이터가 short_url을 기준으로 구성됨
- 데이터의 형식이 다 다를 수 있음(만료 기간 유무)

short_url을 기준으로 구성된 데이터들을 key:value 형식인 redis에 저장하는 것이 데이터 컨셉에 맞다고 생각하였습니다.

또한 만료 기간에 따라 필요 데이터가 달라지기에 value의 값을 넣는데에 자유도가 높은 reids를 선택하였습니다.

### 수평 확장 용이

redis는 클러스터링을 통하여 수평적 확장에 용이합니다.<br>
많은 유져가 유입된다면 클러스터링을 통해 요청을 병렬 처리함으로 더 빠르게 요청을 처리할 수 있습니다.

### 빠른 속도

URL을 Redirect하면 URL을 불러오는데 많은 시간이 걸리게 됩니다.<br>
URL을 Redirect하는 과정에도 많은 시간이 걸리게된다면 사용자경험에 좋지 않을 것이라 판단하여 <br>
메모리에 data를 저장해 빠른 속도로 값을 저장하고 불러오는 redis를 사용하였습니다.

## 단점

redis를 사용함으로써 극복해야할 단점들입니다.

- 메모리 의존성

### 메모리 의존성

Redis는 메모리에서 동작하기에 메모리의 대한 의존이 높습니다.<br>
메모리의 공간에 따라 성능 저하 또는 데이터 손실이 발생 할 수 있습니다.<br>
또한 메모리를 많이 쓰기에 이에 따른 서버 비용 증가를 야기 할 수 있습니다.

#### 해결 방안

조회수, 만료 기간, URL로 이루어진 데이터 중 조회수와 만료기간을 압축하여 4~9byte로 이루어진 데이터 header로 표현하였습니다.<br>
이 방법을 통하여 조회수와 만료 기간을 저장하는 데에 들어가는 비용을 최소화 하였습니다.

##### header 구성

```
처음 4byte
1 ~ 4
00000000 0000000 0000000 0000000 | 0
31bit -> 조회수 | 1bit -> 만료 기간 유무

만료 기간 유무에 따른 5byte
5 ~ 6
00000000 0000 | 0000 |
12bit -> 년도 | 4bit -> 월

7 ~ 9
000000 | 00 0000 | 0000 00 | 000000
6bit -> 일 | 6bit -> 시간 | 6bit -> 분 | 6bit -> 초
```
