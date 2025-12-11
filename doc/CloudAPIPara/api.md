1. 获取人设列表
   Get /api/preset
```bash
curl -X GET 'https://community.nekro.ai/api/preset'
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "ca023aff-8573-494d-b643-578a31ef529c",
        "name": "测试name",
        "title": "测试Title",
        "avatar": "https://oss.nekro.ai/avatars/avatar-af907ba6-f91c-472f-8f6c-d0633abddfed.jpg",
        "content": "测试内容",
        "description": "测试描述",
        "tags": "测试标签1,测试标签2",
        "author": "greenhandzdl",
        "extData": "\"2025-12-11 18:53:43\"",
        "createdAt": "2025-12-11T10:46:42.809Z",
        "updatedAt": "2025-12-11T10:53:46.694Z",
        "isOwner": false
      },
      ...
        ],
    }
}
```

2. 获取人设详情
   Get /api/preset/$id
```bash
curl -X GET 'https://community.nekro.ai/api/preset/$id'
{
  "success": true,
  "data": {
    "id": "ca023aff-8573-494d-b643-578a31ef529c",
    "name": "测试name",
    "title": "测试Title",
    "avatar": "https://oss.nekro.ai/avatars/avatar-af907ba6-f91c-472f-8f6c-d0633abddfed.jpg",
    "content": "测试内容",
    "description": "测试描述",
    "tags": "测试标签1,测试标签2",
    "author": "greenhandzdl",
    "extData": "\"2025-12-11 18:53:43\"",
    "createdAt": "2025-12-11T10:46:42.809Z",
    "updatedAt": "2025-12-11T10:53:46.694Z",
    "isOwner": false
  }
}
```

3.获取用户创建的人设列表
  Get /api/preset/user
```bash
    curl -X GET 'https://community.nekro.ai/api/preset/user' \ 
    -H 'X-API-Key: $API_KEY' \ 
    -H 'Content-Type: application/json'
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "ca023aff-8573-494d-b643-578a31ef529c",
        "name": "测试name",
        "title": "测试Title"
      }
    ],
    "total": 1
  }
}
```

4. 创建人设
  Post /api/preset
```bash
curl -X POST 'https://community.nekro.ai/api/preset' \ 
 -H 'Content-Type: application/json' \ 
 -H 'X-API-Key: $API_KEY' \ 
 -H 'Content-Type: application/json' -d '{
  "name": "$name",
  "title": "$title",
  "avatar": "data:image/jpeg;base64,",
  "content": "$content",
  "description": "$description",
  "tags": "$tags",
  "author": "$author",
  "extData": "$extData",
  "isSfw": $isSfw,
  "instanceId": "$instanceId"
}'

{
  "success": true,
  "data": {
    "id": "43ffeded-ac79-4583-ad66-0ded9176b1ac"
  }
}
```


5. 更新人设
    Put /api/preset/$id
```bash
curl -X PUT 'https://community.nekro.ai/api/preset/$id' \ 
    -H 'Content-Type: application/json' \ 
    -H 'X-API-Key: $API_KEY' \ 
    -H 'Content-Type: application/json' -d '{
  "name": "$name",
  "title": "$title",
  "avatar": "data:image/jpeg;base64,",
  "content": "$content",
  "description": "$description",
  "tags": "$tags",
  "author": "$author",
  "extData": "$extData",
  "isSfw": $isSfw,
  "instanceId": "$instanceId"
}'


6. 删除人设
    Delete /api/preset/$id?instanceId=$instanceId
```bash
curl -X DELETE 'https://community.nekro.ai/api/preset/$id?instanceId=$instanceId'\ 
 -H 'Content-Type: application/json'  \ 
 -H 'X-API-Key: $API_KEY' \ 
```
