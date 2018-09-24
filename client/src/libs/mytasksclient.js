const axios = require('axios')

export default class {
    constructor(auth, authCallback) {
        // load the server from the window, it is exits.
        // this way we can deploy the application without recompiling
        if(window !== undefined && window.MYTASKS_SERVER !== undefined) {
            this.base_url = window.MYTASKS_SERVER
        } else {
            this.base_url = "http://127.0.0.1:5000"
        }

        this.auth = auth
        this.authCallback = authCallback
    }

    get(url) {
        if(!url.startsWith('http')) {
            url = `${this.base_url}${url}`
        }
        console.log(`GET ${url}`)
        return axios.get(url, {auth: this.auth}).catch(error => {
            if(error.response && error.response.status === 401 && this.authCallback !== undefined) {
                this.authCallback()
            }
        })
    }

    post(url, data) {
        if(!url.startsWith('http')) {
            url = `${this.base_url}${url}`
        }
        console.log(`POST ${url}`)
        return axios.post(url, data, {auth: this.auth}).catch(error => {
            if(error.response && error.response.status === 401 && this.authCallback !== undefined) {
                this.authCallback()
            }
        })
    }

    delete(url) {
        if(!url.startsWith('http')) {
            url = `${Mthis.base_url}${url}`
        }
        console.log(`DELETE ${url}`)
        return axios.delete(url, {auth: this.auth}).catch(error => {
            if(error.response && error.response.status === 401 && this.authCallback !== undefined) {
                this.authCallback()
            }
        })
    }

    login(auth) {
        return axios.get(`${this.base_url}/login`, {auth: auth})
    }
}
