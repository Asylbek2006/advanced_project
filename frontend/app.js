const applicationState = {
  accessToken: "",
  currentUserId: null,
  users: [],
  products: [],
  orders: [],
  messages: []
}

const usernameInput = document.getElementById("usernameInput")
const passwordInput = document.getElementById("passwordInput")
const loginButton = document.getElementById("loginButton")
const loginResult = document.getElementById("loginResult")
const sessionState = document.getElementById("sessionState")
const userList = document.getElementById("userList")
const productList = document.getElementById("productList")
const productSelect = document.getElementById("productSelect")
const quantityInput = document.getElementById("quantityInput")
const orderButton = document.getElementById("orderButton")
const orderResult = document.getElementById("orderResult")
const orderList = document.getElementById("orderList")
const receiverSelect = document.getElementById("receiverSelect")
const messageInput = document.getElementById("messageInput")
const sendMessageButton = document.getElementById("sendMessageButton")
const chatResult = document.getElementById("chatResult")
const messageList = document.getElementById("messageList")

async function sendRequest(requestUrl, requestOptions = {}) {
  const finalHeaders = new Headers(requestOptions.headers || {})
  if (applicationState.accessToken) {
    finalHeaders.set("Authorization", `Bearer ${applicationState.accessToken}`)
  }

  const response = await fetch(requestUrl, {
    ...requestOptions,
    headers: finalHeaders
  })

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody.detail || "Request failed")
  }

  return response.json()
}

async function loadInitialData() {
  await Promise.all([
    loadUsers(),
    loadProducts()
  ])
}

async function loadUsers() {
  applicationState.users = await sendRequest("/api/users/users")
  renderUsers()
  renderReceiverOptions()
}

async function loadProducts() {
  applicationState.products = await sendRequest("/api/products/products")
  renderProducts()
  renderProductOptions()
}

async function loadOrders() {
  if (!applicationState.accessToken) {
    orderList.innerHTML = ""
    return
  }

  applicationState.orders = await sendRequest("/api/orders/orders")
  renderOrders()
}

async function loadMessages() {
  if (!applicationState.accessToken) {
    messageList.innerHTML = ""
    return
  }

  applicationState.messages = await sendRequest("/api/chat/messages")
  renderMessages()
}

function renderUsers() {
  userList.innerHTML = applicationState.users
    .map((userProfile) => `
      <div class="list_item">
        <strong>${userProfile.full_name}</strong><br>
        <span>${userProfile.email}</span><br>
        <span>${userProfile.department}</span>
      </div>
    `)
    .join("")
}

function renderProducts() {
  productList.innerHTML = applicationState.products
    .map((productItem) => `
      <div class="product_card">
        <strong>${productItem.name}</strong>
        <p>${productItem.description}</p>
        <div class="product_price">$${productItem.price.toFixed(2)}</div>
        <div>Stock: ${productItem.stock_quantity}</div>
      </div>
    `)
    .join("")
}

function renderProductOptions() {
  productSelect.innerHTML = applicationState.products
    .map((productItem) => `<option value="${productItem.id}">${productItem.name}</option>`)
    .join("")
}

function renderReceiverOptions() {
  receiverSelect.innerHTML = applicationState.users
    .filter((userProfile) => userProfile.id !== applicationState.currentUserId)
    .map((userProfile) => `<option value="${userProfile.id}">${userProfile.full_name}</option>`)
    .join("")
}

function renderOrders() {
  orderList.innerHTML = applicationState.orders
    .map((orderItem) => `
      <div class="list_item">
        <strong>Order #${orderItem.id}</strong><br>
        <span>User ID: ${orderItem.user_id}</span><br>
        <span>Product ID: ${orderItem.product_id}</span><br>
        <span>Quantity: ${orderItem.quantity}</span><br>
        <span>Total: $${orderItem.total_price.toFixed(2)}</span><br>
        <span>Status: ${orderItem.status}</span>
      </div>
    `)
    .join("")
}

function renderMessages() {
  messageList.innerHTML = applicationState.messages
    .map((messageItem) => `
      <div class="list_item">
        <strong>${messageItem.sender_user_id} -> ${messageItem.receiver_user_id}</strong><br>
        <span>${messageItem.message_text}</span>
      </div>
    `)
    .join("")
}

async function handleLoginClick() {
  loginResult.textContent = ""
  try {
    const loginResponse = await sendRequest("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: usernameInput.value.trim(),
        password: passwordInput.value.trim()
      })
    })

    applicationState.accessToken = loginResponse.access_token
    applicationState.currentUserId = loginResponse.user_id
    sessionState.textContent = `Logged in as ${loginResponse.full_name}`
    loginResult.textContent = "Login successful"
    renderReceiverOptions()
    await Promise.all([loadOrders(), loadMessages()])
  } catch (requestError) {
    applicationState.accessToken = ""
    applicationState.currentUserId = null
    sessionState.textContent = "Logged out"
    loginResult.textContent = requestError.message
  }
}

async function handleOrderClick() {
  orderResult.textContent = ""
  try {
    const createdOrder = await sendRequest("/api/orders/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        product_id: Number(productSelect.value),
        quantity: Number(quantityInput.value)
      })
    })

    orderResult.textContent = `Order ${createdOrder.id} created`
    await loadOrders()
  } catch (requestError) {
    orderResult.textContent = requestError.message
  }
}

async function handleSendMessageClick() {
  chatResult.textContent = ""
  try {
    const createdMessage = await sendRequest("/api/chat/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        receiver_user_id: Number(receiverSelect.value),
        message_text: messageInput.value.trim()
      })
    })

    chatResult.textContent = `Message ${createdMessage.id} sent`
    messageInput.value = ""
    await loadMessages()
  } catch (requestError) {
    chatResult.textContent = requestError.message
  }
}

loginButton.addEventListener("click", handleLoginClick)
orderButton.addEventListener("click", handleOrderClick)
sendMessageButton.addEventListener("click", handleSendMessageClick)

loadInitialData()

