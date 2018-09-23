const axios = require('axios')

export default class {
    constructor(baseurl, auth, authCallback) {
        this.baseurl = baseurl
        this.auth = auth
        this.authCallback = authCallback
    }

    get(url) {
        if(!url.startsWith('http')) {
            url = `${this.baseurl}${url}`
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
            url = `${this.baseurl}${url}`
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
            url = `${this.baseurl}${url}`
        }
        console.log(`DELETE ${url}`)
        return axios.delete(url, {auth: this.auth}).catch(error => {
            if(error.response && error.response.status === 401 && this.authCallback !== undefined) {
                this.authCallback()
            }
        })
    }

    login(auth) {
        return axios.get(`${this.baseurl}/login`, {auth: auth})
    }
}
