import React, { useState, useRef, useEffect } from "react";
import "vis-timeline/styles/vis-timeline-graph2d.css";
import moment from "moment"
import { Chart } from "react-google-charts";
import { MultiSelect } from "react-multi-select-component";

const companyjson = require('./data/companies.json'); 
const eventsjson = require('./data/announcements.json');      
const patentjson = require('./data/patents.json');


function Visualization() {
    const [timelineData, setTimelineData] = useState()
    const [selected, setSelected] = useState([]);
    const [visOptions, setOptions] = useState([])
    
    const columns = [
        { type: "string", id: "Company" },
        { type: "string", id: "Name" },
        { type: "datetime", id: "Start" },
        { type: "datetime", id: "End" }
    ];

    useEffect(() => {
        var options = []
        // get companies that have patents
        var uniquePatentComp = [...new Set(patentjson.map(elem => elem["company_reference"]))]
        var companies = uniquePatentComp.map(elem => companyjson.filter(e => e["reference_id"] + "_" + e["local_court"] === elem)[0]["name"])
        for (var comp of companies) {
            options.push({label: comp, value: comp})
        }
        setOptions(options)
    },[])

    useEffect(() => {
        var rows = []
        
        var selectedCompanies = selected.map(el => el["value"])
        for (var comp in selectedCompanies) {
            var companyEntries = companyjson.filter(function (el) {
                return el["name"] === selectedCompanies[comp]
            });
            var a_entry_ids = companyEntries.map(elem => elem["id"].replace("bw_", ""))
            var p_entry_id = companyEntries[0]["reference_id"] + "_" + companyEntries[0]["local_court"]
            for (var i in a_entry_ids) {
                var a_entries = eventsjson.filter(function (el) {
                    return el["rb_id"].toString() === a_entry_ids[i]
                })

                var start = moment(a_entries[0]["event_date"], "DD-MM-YYYY")         
                rows.push([selectedCompanies[comp], a_entries[0]["event_type"], start, start])
            }

            var p_entries = patentjson.filter(function (el) {
                return el["company_reference"].toString() === p_entry_id
            })
            for (var k in p_entries) {
                var start = moment(p_entries[k]["publication_date"], "DD-MM-YYYY")          
                rows.push([selectedCompanies[comp], "Patent", start, start]) //p_entries[k]["title"]
            }
            
        }
        const data = [columns, ...rows];
        setTimelineData(data)
    }, [selected])
    
   
    return (
        <div style={{padding: "20px", height:"80vh"}}>
            <div style={{paddingBottom: "20px"}}>
                <MultiSelect
                    options={visOptions}
                    value={selected}
                    onChange={setSelected}
                    labelledBy="Select" />
            </div>
            
            {selected.length > 0 && <Chart
                chartType="Timeline"
                data={timelineData}
                width="100%"
                height="100%"/>}
        </div>
    );
}

export default Visualization;
