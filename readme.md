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
