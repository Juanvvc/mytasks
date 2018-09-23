const axios = require('axios')

export default class {
    constructor(baseurl, auth) {
        this.baseurl = baseurl
        this.auth = auth
    }

    get(url) {
        if(url.startsWith('http')) {
            console.log(`GET ${url}`)
            return axios.get(url, {auth: this.auth})
        } else {
            console.log(`GET ${this.baseurl}/${url}`)
            return axios.get(`${this.baseurl}/${url}`, {auth: this.auth})
        }
    }

    post(url, data) {
        if(url.startsWith('http')) {
            console.log(`POST ${url}`)
            return axios.post(url, data, {auth: this.auth})
        } else {
            console.log(`POST ${this.baseurl}/${url}`)
            return axios.post(`${this.baseurl}/${url}`, data, {auth: this.auth})
        }
    }

    delete(url) {
        if(url.startsWith('http')) {
            console.log(`DELETE ${url}`)
            return axios.delete(url, {auth: this.auth})
        } else {
            console.log(`DELETE ${this.baseurl}/${url}`)
            return axios.delete(`${this.baseurl}/${url}`, {auth: this.auth})
        }
    }

    login(auth) {
        this.auth = auth
        return axios.get(`${this.baseurl}/login`, {auth: this.auth})
    }
}
