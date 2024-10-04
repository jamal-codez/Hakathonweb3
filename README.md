### Log in

```http
  POST /api/login/
```
#### Headers
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |

#### Parameters
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `email` | `string` | **Required**. The User email |
| `password` | `string` | **Required**. The User password |

#### Success Response
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `id` | `int` |    The User Unique Id |
| `fullname` | `string` |  The User email |
| `email` | `string` |    The User password |
| `token` | `string` |    The User authentication token for passing to Headers for api authentication |
| `is_active` | `bool` |    The flag for active user |
| `is_staff` | `bool` |    The flag for staff user check |
| `is_superuser` | `bool` |    The flag for superuser check |
| `date_joined` | `datetime` |    The date the account was created 
| `last_login` | `datetime` |    The last login date of the account |

#### Error Response
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `message` | `string` |    The Error Message |




### Register

```http
  POST /api/register/
```
#### Headers
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |

#### Parameters
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `full_name` | `string` | **Required**. The User's fullname |
| `email` | `string` | **Required**. The User's email |
| `phone_number` | `string` | **Required**. The User's phone number |
| `password` | `string` | **Required**. The User's password |

#### Success Response
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `message` | `created` |    


#### Error Response
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `message` | `string` |    The Error Message |
| `fullname` | `string or list` | **Optional** |
| `email` | `string or list` | **Optional** |
| `phone_number` | `string or list` | **Optional** |
| `password` | `string or list` | **Optional** |



### Get User's cGroups

```http
  GET /api/my-groups/
```
#### Headers
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | **Required**. The auth token for verifiy the user: Format: `Token ${token}` |

#### Parameters
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |

#### Success Response
#### List of objects
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `id` | `int` | The id of the community |
| `name` | `string` | The name of the community |
| `description` | `string` | The description of the community |
| `picture` | `string` | The banner image of the community |
| `chat_id` | `string` | The Chat Id of the community |
| `date_created` | `date` | The date the community was created |



### View Group messages
```http
  GET /api/solarigroup/${id}/messages/
```
#### Headers
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | **Required**. The auth token for verifiy the user: Format: `Token ${token}` |

#### Url Parameters
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `int` | **Required**. The Id of the group |


#### Success Response
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |

#### List of messages objects
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `id` | `int` | The id of the message |
| `chatspace` | `string` | The id of the chatspace |
| `type` | `string` | The type of the message. options: `audio`, `text`, `document`, `image` |
| `sender` | `object` | `keys`: `id`,`fullname`,`email` |
| `content` | `string` | The message text. can be nul |
| `file` | `string` | The url to the file of selected type. can be ull |
| `date_created` | `date` | The date message was created |





### List of User personal chats
```http
  GET /api/chats/
```
#### Headers
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | **Required**. The auth token for verifiy the user: Format: `Token ${token}` |


#### Success Response
#### List of objects
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `id` | `string` | The id of the chat |
| `chat_name` | `string` | The name of the chat |







### Start a personal chats
```http
  GET /api/chats/start/
```
#### Headers
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `string` | **Required**. The auth token for verifiy the user: Format: `Token ${token}` |

#### Parameters
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user` | `int` | The Id of the user to start the chat with|


#### Success Response
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `id` | `string` | The id of the chat |
| `chat_name` | `string` | The name of the chat |


