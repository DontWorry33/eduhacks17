// register the grid component
Vue.component('demo-grid', {
    template: '#grid-template',
    props: {
        data: Array,
        columns: Array,
        filterKey: String
    },
    data: function() {
        var sortOrders = {}
        this.columns.forEach(function(key) {
            sortOrders[key] = 1
        })
        return {
            sortKey: '',
            sortOrders: sortOrders
        }
    },
    computed: {
        filteredData: function() {
            var sortKey = this.sortKey
            var filterKey = this.filterKey && this.filterKey.toLowerCase()
            var order = this.sortOrders[sortKey] || 1
            var data = this.data
            if (filterKey) {
                data = data.filter(function(row) {
                    return Object.keys(row).some(function(key) {
                        return String(row[key]).toLowerCase().indexOf(filterKey) > -1
                    })
                })
            }
            if (sortKey) {
                data = data.slice().sort(function(a, b) {
                    a = a[sortKey]
                    b = b[sortKey]
                    return (a === b ? 0 : a > b ? 1 : -1) * order
                })
            }
            return data
        }
    },
    filters: {
        capitalize: function(str) {
            return str.charAt(0).toUpperCase() + str.slice(1)
        }
    },
    methods: {
        sortBy: function(key) {
            this.sortKey = key
            this.sortOrders[key] = this.sortOrders[key] * -1
        }
    }
})

// bootstrap the demo
var demo = new Vue({
    el: '#demo',
    data: {
        searchQuery: '',
        gridColumns: ['name', 'completed', 'passed', 'time'],
        gridData: [
            { name: 'Chuck Norris', completed: 3, passed: true, time: '1:00' },
            { name: 'Bruce Lee', completed: 2, passed: true, time: '1:23' },
            { name: 'Jackie Chan', completed: 2, passed: true, time: '1:34' },
            { name: 'Jet Li', completed: 1, passed: false, time: '2:34' },
            { name: 'Floyd Mayweather', completed: 0, passed: false, time: '5:00' },
            { name: 'Scooby-doo', completed: 0, passed: false, time: '4:23' },
            { name: 'The gang', completed: 1, passed: false, time: '4:14' },
            { name: 'Jason Chan', completed: 0, passed: false, time: '20:34' }
        ]
    }
})
