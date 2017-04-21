# wxapp
wxapp django for wafer 

# database
name: wxapp

# app
name: wafer
function: save wxapp login session info

## 模型设计

`AppInfo` 保存会话服务所需要的配置项。

<table>
  <tbody>
  <tr>
    <th>Field</th>
    <th>Type</th>
    <th>Null</th>
    <th>key</th>
    <th>Extra</th>
  </tr>
  <tr>
    <td>title</td>
    <td>varchar(30)</td>
    <td>NO</td>
    <td>NO</td>
    <td>小程序名称</td>
  </tr>
  <tr>
    <td>appid</td>
    <td>varchar(200)</td>
    <td>NO</td>
    <td></td>
    <td>申请微信小程序开发者时，微信分配的 appId</td>
  </tr>
  <tr>
    <td>secret</td>
    <td>varchar(300)</td>
    <td>NO</td>
    <td></td>
    <td>申请微信小程序开发者时，微信分配的 appSecret</td>
  </tr>
  <tr>
    <td>login_duration</td>
    <td>int(11)</td>
    <td>NO</td>
    <td></td>
    <td>登录过期时间，单位为天，默认 30 天</td>
  </tr>
  <tr>
    <td>session_duration</td>
    <td>int(11)</td>
    <td>NO</td>
    <td></td>
    <td>会话过期时间，单位为秒，默认为 2592000 秒(即30天)</td>
  </tr>
  
  </tbody>
</table>
    

会话记录 `SessionInfo` 保存每个会话的数据。

<table>
  <tbody>
  <tr>
    <th>Field</th>
    <th>Type</th>
    <th>Null</th>
    <th>key</th>
    <th>Extra</th>
  </tr>
  <tr>
    <td>uuid</td>
    <td>varchar(100)</td>
    <td>NO</td>
    <td></td>
    <td>会话 uuid</td>
  </tr>
  <tr>
    <td>skey</td>
    <td>varchar(100)</td>
    <td>NO</td>
    <td></td>
    <td>会话 Skey</td>
  </tr>
  <tr>
    <td>create_time</td>
    <td>datetime</td>
    <td>NO</td>
    <td></td>
    <td>会话创建时间，用于判断会话对应的 open_id 和 session_key 是否过期（是否超过 `cAppInfo` 表中字段 `login_duration` 配置的天数）</td>
  </tr>
  <tr>
    <td>last_visit_time</td>
    <td>datetime</td>
    <td>NO</td>
    <td></td>
    <td>最近访问时间，用于判断会话是否过期（是否超过 `cAppInfo` 表中字段 `session_duration` 的配置的秒数）</td>
  </tr>
  <tr>
    <td>open_id</td>
    <td>varchar(100)</td>
    <td>NO</td>
    <td>MUL</td>
    <td>微信服务端返回的 `open_id` 值 </td>
  </tr>
  <tr>
    <td>session_key</td>
    <td>varchar(100)</td>
    <td>NO</td>
    <td></td>
    <td>微信服务端返回的 `session_key` 值 </td>
  </tr>
  <tr>
    <td>user_info</td>
    <td>varchar(2048)</td>
    <td>YES</td>
    <td></td>
    <td>已解密的用户数据</td>
  </tr>
  </tbody>
</table>

## 接口协议

### 请求

会话服务器提供 HTTP 接口来实现会话管理，下面是协议说明。

* 协议类型：`HTTP`
* 传输方式：`POST`
* 编码类型：`UTF-8`
* 编码格式：`JSON`

请求示例：

### mina/login

`mina/login` 处理用户登录请求。

请求数据：

* `code` - 微信小程序客户端获取的code
* `encrypt_data` - 微信小程序客户端获取的encryptedData，可为空
* `iv` - 微信小程序客户端获取的解密iv，可为空
* `app_id` - 所属小程序的id（数据库中存储的主键id）

使用示例：

```js
function login_server(loginResult, userResult) {
  var app = getApp();
  wx.request({
    url: config.s_url+'login',
    data: {code: loginResult.code, encrypt_data: userResult.encryptedData, iv: userResult.iv, app_id:app.globalData.app_id},
    method: 'POST', 
    success: function(res){
      if(res.data.ok=='success') {
        wx.setStorageSync('skey', res.data.data.skey);
        wx.setStorageSync('uuid', res.data.data.uuid)
        console.log(res.data.msg||'成功获取授权数据');
      } else {
        login();
      }
    },
    fail: function() {
      console.log('get skey error');
    }
  });
}
function login() {
  wx.login({
    success: function (loginResult) {
      wx.getUserInfo({
        success: function (userResult) {
          //app.globalData.userInfo = userResult.userInfo;
          login_server(loginResult, userResult);
        },
        fail: function () {
          console.log('用户未同意授权');
          var userResult = {encrypt_data:'', iv:''};
          login_server(loginResult, userResult);
        }
      })
    },
    fail: function() {
      tip('微信用户未登录，部分功能无法使用!');
    }
  });
}
```

响应数据：

* `ok` - 请求成功（success）或失败（fail）
* `msg` - 成功提示或失败原因
* `data` - {`uuid`, `skey`, `user_info`, `duration`}

### mina/auth

使用 `mina/auth` 接口检查用户登录状态。

请求数据：

* `uuid` - 微信小程序客户端`Storage[uuid]`
* `skey` - 微信小程序客户端`Storage[skey]`
* `app_id` - 所属小程序的id（数据库中存储的主键id）


使用示例：

(每次业务操作均验证`skey`、`uuid`，建议在业务服务中向`mina/auth`发起请求)

```js
  load_fan: function () {
    var that = this;
    var app_id= app.globalData.app_id;
    var skey = wx.getStorageSync('skey');
    var uuid = wx.getStorageSync('uuid');
    wx.request({
      url: config.base_url+'fan',
      data: {app_id: app_id, skey: skey, uuid: uuid},
      method: 'POST', 
      success: function(res){
        if (res.data.ok == 'success') {
          var f = res.data.f;
          that.setData({user:f});
          console.log(res.data.msg||'成功获取用户信息');
        }
      },
      fail: function() {
        util.tip('load user name and mobile fail');
      }
    });
  }
```

响应数据：

* `ok` - 请求成功（success）或失败（fail）
* `msg` - 成功提示或失败原因
* `data` - {`user_info`}
