const axios = require('axios')

class MyTasks {
    constructor () {
        // load the server from the window, it is exits.
        // this way we can deploy the application without recompiling
        if(window !== undefined && window.MYTASKS_SERVER !== undefined) {
            this.base_url = window.MYTASKS_SERVER
        } else {
            this.base_url = "http://127.0.0.1:5000"
        }
    }

    onError(errorCallback) {
        this.errorCallback = errorCallback
    }

    manageError(error) {
        if(error.response) {
            if(error.response.status === 401 && this.authCallback !== undefined) {
                this.authCallback()
            } else if(this.errorCallback !== undefined){
                this.errorCallback(error.response.message)
            } else {
                throw error
            }
        } else {
            if(this.errorCallback !== undefined ) {
                this.errorCallback('Unknown error connecting to the server')
            } else {
                throw error
            }
        }
    }

    setAuth(auth, authCallback) {
        this.auth = auth
        this.authCallback = authCallback
    }

    get(url) {
        if(!url.startsWith('http')) {
            url = `${this.base_url}${url}`
        }
        console.log(`GET ${url}`)
        return axios.get(url, {auth: this.auth}).then(response =>{
            if(response.error_message !== undefined) {
                throw new Error(response)
            } else {
                return response
            }
        }, error => {
            this.manageError(error)
        })
    }

    post(url, data) {
        if(!url.startsWith('http')) {
            url = `${this.base_url}${url}`
        }
        console.log(`POST ${url}`)
        return axios.post(url, data, {auth: this.auth}).then(response =>{
            if(response.error_message !== undefined) {
                throw new Error(response)
            } else {
                return response
            }
        }, error => {
            this.manageError(error)
        })
    }

    delete(url) {
        if(!url.startsWith('http')) {
            url = `${this.base_url}${url}`
        }
        console.log(`DELETE ${url}`)
        return axios.delete(url, {auth: this.auth}).then(response =>{
            if(response.error_message !== undefined) {
                throw new Error(response)
            } else {
                return response
            }
        }, error => {
            this.manageError(error)
        })
    }

    login(auth) {
        return axios.get(`${this.base_url}/login`, {auth: auth})
    }
}

var client = new MyTasks()

export default client
