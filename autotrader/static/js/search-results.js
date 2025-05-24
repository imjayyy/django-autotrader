
document.addEventListener("DOMContentLoaded", function() {
    let params = getQueryParams();
    const windowWidth = window.innerWidth

    if (windowWidth > 767){
        // Remove mobile filters from desktop
        document.getElementById("mobile-filters-modal").innerHTML = "";
    }else{
        document.getElementById("filterMobileMakeTrigger").innerHTML = mobileFilterTemplateEngine("Vehicle Make", [], "mobileFilterMake", "filterMobileMakeTrigger", "make")
        document.getElementById("filterMobileModelTrigger").innerHTML = mobileFilterTemplateEngine("Model", [], "mobileFilterModel", "filterMobileModelTrigger", "model")
        document.getElementById("filterMobileEngineTypeTrigger").innerHTML = mobileFilterTemplateEngine("Engine Type", [], "mobileFilterEngineType","filterMobileEngineTypeTrigger","engine_type")
        document.getElementById("filterMobileTransmissionTrigger").innerHTML = mobileFilterTemplateEngine("Transmission", [], "mobileFilterTransmission", "filterMobileTransmissionTrigger", "transmission")
        document.getElementById("filterMobileFuelTrigger").innerHTML = mobileFilterTemplateEngine("Fuel Type", [], "mobileFilterFuelType", "filterMobileFuelTrigger", "fuel")
        document.getElementById("filterMobileDriveTrigger").innerHTML = mobileFilterTemplateEngine("Drive", [], "mobileFilterDrive", "filterMobileDriveTrigger", "Drive")
        document.getElementById("filterMobileBodyStyleTrigger").innerHTML = mobileFilterTemplateEngine("Body Style", [], "mobileFilterBodyStyle", "filterMobileBodyStyleTrigger", "BodyStyle")
        document.getElementById("filterMobileCountryTrigger").innerHTML = mobileFilterTemplateEngine("Country", [], "mobileFilterCountry", "filterMobileCountryTrigger", "country")

        document.getElementById("filterMobileOdometerTrigger").innerHTML = mobileFilterTemplateEngine("Odometer", [], "mobileFilterOdometer", "filterMobileOdometerTrigger", "")
        document.getElementById("filterMobilePriceTrigger").innerHTML = mobileFilterTemplateEngine("Price", [], "mobileFilterPrice", "filterMobilePriceTrigger", "")
        document.getElementById("filterMobileYearTrigger").innerHTML = mobileFilterTemplateEngine("Year", [], "mobileFilterYear", "filterMobileYearTrigger", "")

    }
    console.log(params);    
    // if ("searchByText" in params) {
    //     console.log("Search value:", params.searchByText);
    //     return
    // }
    params.make = params.make ? params.make.split(",") : [];
    params.model = params.model ? params.model.split(",") : [];

    console.log("params:", params);

    //Updating initial mobile filters
    //     `
    //      <h2 class="accordion-header">
    //                                     <a
    //                                             class="text-heading text-secondary-color d-flex justify-content-between align-items-center"
    //                                             type="button"
    //                                             data-bs-toggle="modal"
    //                                             data-bs-target="#mobileFilterMake"
    //                                     >
    //                                         <span>Vehicle Make</span>
    //                                         <i class="bi bi-chevron-right text-secondary-color" style="font-size: 20px;"></i>
    //                                     </a>
    //                                 </h2>
    // `;

    let selectMake = document.querySelectorAll(`input[name="make"]`);
    selectMake.forEach((element) => {
        for (let i = 0; i < params.make.length; i++) {
            if (params.make[i] === element.value) {
                // element.checked = true;
                if (windowWidth > 767){
                    document.getElementById(`make_${element.value}`).checked = true
                }else{
                    document.getElementById(`mobile_make_${element.value}`).checked = true
                }


                // console.log(element,"element")
                // console.log(document.getElementById(element.id),"document.getElementById(element.id)")
                // document.getElementById(element.id).checked = true;
             }
        }
    });

    Object.entries(params).forEach(([key, value]) => {
        let input_form_elements = document.querySelectorAll(`input[name="${key}"]`);
        input_form_elements.forEach((input_form_element) => {
            if (input_form_element) {
                if (input_form_element.type === "checkbox") {
                    if(input_form_element.value === value){
                        // console.log(input_form_element.name,"ss")
                        // document.getElementById(input_form_element.id).checked = true;
                    input_form_element.checked = true;
                        }
                }
                else {
                    input_form_element.value = value;
                }
            }
        });
    });
        
    

    Promise.resolve(update_models()).then(() => {
        setTimeout(() => {
            let selectModel = document.querySelectorAll(`input[name="model"]`);

            selectModel.forEach((element) => {
                for (let i = 0; i < params.model.length; i++) {
                        if (params.model[i] === element.value) {
                            document.getElementById(`model_${element.value}`).checked = true;
                            // element.checked = true;
                        }
                }
            });
            update_cars_data();

            if (windowWidth <= 767){

                // initial model list
                let selectedModels_for_filter = [];
                let selectedModelNames = []
                document.querySelectorAll('input[name="model"]:checked').forEach((checkbox) => {
                    selectedModels_for_filter.push(checkbox.value);
                });
                selectedModels_for_filter = removeDuplicates(selectedModels_for_filter)

                selectedModels_for_filter.forEach(selectedModel => {
                    const currentElementNames = document.getElementById(`model_${selectedModel}`).getAttribute("name-attr")
                    selectedModelNames.push(currentElementNames)
                })
                document.getElementById("filterMobileModelTrigger").innerHTML = mobileFilterTemplateEngine("Model", selectedModelNames, "mobileFilterModel", "filterMobileModelTrigger", "model")

            }
        }, 500); // Delay for 500ms to ensure models are loaded
    });

});



function change_accordion_text(accordion_id) {
    const button = document.getElementById(accordion_id);
    const toggleText = button.querySelector(".toggle-text");    
    if (toggleText.textContent === "More Details") {
        toggleText.textContent = "Less Details";
    } 
    else {
        toggleText.textContent = "More Details"
    }
}



function getQueryParams() {
    const params = new URLSearchParams(window.location.search);
    let queryObject = {};
    
    params.forEach((value, key) => {
        if (queryObject[key]) {
            // Convert to array if multiple values exist for the same key
            queryObject[key] = [].concat(queryObject[key], value);
        } else {
            queryObject[key] = value;
        }
    });

    return queryObject;
}


function removeDuplicates(array, byKey){
    let duplicate = array;
    if (byKey){
        duplicate = duplicate.map(el => el[byKey])
    }
    return array.filter((item, index) => duplicate.indexOf(byKey ? item[byKey] : item) === index)
}
function update_filters(){
    let selectedMakes_for_filter = [];
    let selectedModels_for_filter = [];

    document.querySelectorAll('input[name="make"]:checked').forEach((checkbox) => {
        selectedMakes_for_filter.push(checkbox.value);
    });
    selectedMakes_for_filter = removeDuplicates(selectedMakes_for_filter)

    document.querySelectorAll('input[name="model"]:checked').forEach((checkbox2) => {
        selectedModels_for_filter.push(checkbox2.value);
    });
    selectedModels_for_filter = removeDuplicates(selectedModels_for_filter)


    window.location.href = "/search-results" + "?make=" + selectedMakes_for_filter.join(",") + "&model=" + selectedModels_for_filter.join(",");
    return;
}


function sortBy() {
      const sortBtn = document.getElementById('sortBtn');

        const currentOrder = sortBtn.getAttribute('data-order');
        const tooltip = new bootstrap.Tooltip(sortBtn);

        if (currentOrder === 'asc') {
        sortBtn.setAttribute('data-order', 'desc');
        sortBtn.classList.remove('btn-outline-danger');
        sortBtn.classList.add('btn-danger');
        sortBtn.setAttribute('title', 'Sort Descending');

        } else {
        sortBtn.setAttribute('data-order', 'asc');
        sortBtn.classList.remove('btn-danger');
        sortBtn.classList.add('btn-outline-danger');
        sortBtn.setAttribute('title', 'Sort Ascending');

        }
        tooltip.setContent({ '.tooltip-inner': sortBtn.getAttribute('title') });

        // Optional: Use the value somewhere
        console.log('Sort Order:', sortBtn.getAttribute('data-order'));

        update_cars_data();

}



function update_cars_data(page=1){


    const windowWidth = window.innerWidth
    let selectedMakes = [];
    let selectedMakesNames = []
    document.querySelectorAll('input[name="make"]:checked').forEach((checkbox) => {
        selectedMakes.push(checkbox.value);
        selectedMakesNames.push( {"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')} );
    });



    let selectedModels = [];
    let selectedModelsNames = []
    document.querySelectorAll('input[name="model"]:checked').forEach((checkbox) => {
        selectedModels.push(checkbox.value);
        selectedModelsNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });

    let selectedTransmissions = [];
    let selectedTransmissionsNames = []
    document.querySelectorAll('input[name="Transmission"]:checked').forEach((checkbox) => {
        selectedTransmissions.push(checkbox.value);
        selectedTransmissionsNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });

    let selectedDrives = [];
    let selectedDrivesNames = []
    document.querySelectorAll('input[name="Drive"]:checked').forEach((checkbox) => {
        selectedDrives.push(checkbox.value);
        selectedDrivesNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });


    let selectedFuels = [];
    let selectedFuelsNames = []
    document.querySelectorAll('input[name="fuel"]:checked').forEach((checkbox) => {
        selectedFuels.push(checkbox.value);
        selectedFuelsNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });


    let selectedBodyStyles = [];
    let selectedBodyStylesNames = []
    document.querySelectorAll('input[name="BodyStyle"]:checked').forEach((checkbox) => {
        selectedBodyStyles.push(checkbox.value);
        selectedBodyStylesNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });


    let selectedCountries = [];
    let selectedCountriesNames = []
    document.querySelectorAll('input[name="country"]:checked').forEach((checkbox) => {
        selectedCountries.push(checkbox.value);
        selectedCountriesNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });

    let selectedColors = [];
    let selectedColorsNames = []
    document.querySelectorAll('input[name="color"]:checked').forEach((checkbox) => {
        selectedColors.push(checkbox.value);
        selectedColorsNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });

    let selectedEngineTypes = [];
    let selectedEngineTypesNames = []
    document.querySelectorAll('input[name="engine_type"]:checked').forEach((checkbox) => {
        selectedEngineTypes.push(checkbox.value);
        selectedEngineTypesNames.push({"id": checkbox.value,  "name": checkbox.getAttribute('name-attr')});
    });



    let odometerMin;
    let odometerMax;

    let priceMin;
    let priceMax;


    let year_min;
    let year_max;

    if (windowWidth <= 767){
        document.getElementById("filterMobileTransmissionTrigger").innerHTML = mobileFilterTemplateEngine("Transmission", selectedTransmissionsNames.map(el => el.name), "mobileFilterTransmission", "filterMobileTransmissionTrigger", "transmission")
        document.getElementById("filterMobileDriveTrigger").innerHTML = mobileFilterTemplateEngine("Drive", selectedDrivesNames.map(el => el.name), "mobileFilterDrive", "filterMobileDriveTrigger", "Drive")
        document.getElementById("filterMobileFuelTrigger").innerHTML = mobileFilterTemplateEngine("Fuel Type", selectedFuelsNames.map(el => el.name), "mobileFilterFuelType", "filterMobileFuelTrigger", "fuel")
        document.getElementById("filterMobileBodyStyleTrigger").innerHTML = mobileFilterTemplateEngine("Body Style", selectedBodyStylesNames.map(el => el.name), "mobileFilterBodyStyle", "filterMobileBodyStyleTrigger", "BodyStyle")
        document.getElementById("filterMobileCountryTrigger").innerHTML = mobileFilterTemplateEngine("Country", selectedCountriesNames.map(el => el.name), "mobileFilterCountry", "filterMobileCountryTrigger", "country")
        document.getElementById("filterMobileEngineTypeTrigger").innerHTML = mobileFilterTemplateEngine("Engine Type", selectedEngineTypesNames.map(el => el.name), "mobileFilterEngineType", "filterMobileEngineTypeTrigger", "engine_type")

        odometerMin = document.querySelector('input[id="odometer_min_mobile"]').value;
        odometerMax = document.querySelector('input[id="odometer_max_mobile"]').value;

        priceMin = document.querySelector('input[id="price_min_mobile"]').value;
        priceMax = document.querySelector('input[id="price_max_mobile"]').value;

        year_min = document.querySelector('input[id="year_min_mobile"]').value;
        year_max = document.querySelector('input[id="year_max_mobile"]').value;



        document.getElementById("filterMobileOdometerTrigger").innerHTML = mobileFilterTemplateEngine("Odometer", odometerMin || odometerMax ? [`${odometerMin || 0}-${odometerMax || 0}`] : [], "mobileFilterOdometer", "filterMobileOdometerTrigger", "")
        document.getElementById("filterMobilePriceTrigger").innerHTML = mobileFilterTemplateEngine("Price", priceMin || priceMax ? [`${priceMin || 0}-${priceMax || 0}`] : [], "mobileFilterPrice", "filterMobilePriceTrigger", "")
        document.getElementById("filterMobileYearTrigger").innerHTML = mobileFilterTemplateEngine("Year", year_min || year_max ? [`${year_min || 0}-${year_max || 0}`] : [], "mobileFilterYear", "filterMobileYearTrigger", "")

        // alert("Values Successfully Updated")
    }else{
        odometerMin = document.querySelector('input[id="odometer_min"]').value;
        odometerMax = document.querySelector('input[id="odometer_max"]').value;

        priceMin = document.querySelector('input[id="price_min"]').value;
        priceMax = document.querySelector('input[id="price_max"]').value;

        year_min = document.querySelector('input[id="year_min"]').value;
        year_max = document.querySelector('input[id="year_max"]').value;
    }


    let sorting_by = document.getElementById('sortBy').value;
    let sorting_order = document.getElementById('sortBtn').getAttribute('data-order');


    let filterParams = {
        page: page,
        make: removeDuplicates(selectedMakes),
        model: removeDuplicates(selectedModels),
        transmission: selectedTransmissions,
        drives: selectedDrives,
        fuels: selectedFuels,
        body_style: selectedBodyStyles,
        odometerMin: odometerMin,
        odometerMax: odometerMax,
        priceMin: priceMin,
        priceMax: priceMax,
        country: selectedCountries,
        color: selectedColors,
        year_min: year_min,
        year_max: year_max,

        sorting_by: sorting_by,
        sorting_order: sorting_order,
        engine_type: selectedEngineTypes,

    };

    let filterTags = {
        "make": removeDuplicates(selectedMakesNames, "id"),
        "model": removeDuplicates(selectedModelsNames, "id"),
        "Transmission": selectedTransmissionsNames,
        "Drive": selectedDrivesNames,
        "fuel": selectedFuelsNames,
        "BodyStyle": selectedBodyStylesNames,
        "country": selectedCountriesNames,
        "color": selectedColors,
        "odometer_min": odometerMin,
        "odometer_max": odometerMax,
        "price_min": priceMin,
        "price_max": priceMax,
        "year_min": year_min,
        "year_max": year_max,
        "engine_type": selectedEngineTypesNames,
    }

    console.log("filterTags:", filterTags);

    axios.get('/api/search-api/', {
        params: filterParams
    })
    .then(function (response) {
        console.log("resp:", response.data);
        if (response.data.count === 0 ){
            document.getElementById("table_results").innerHTML = `<div class="alert alert-danger" role="alert">
            No results found for your search. Please try again with different filters.
            </div>`;
            document.getElementById("table_results_mobile").innerHTML = `<div class="alert alert-danger" role="alert">
            No results found for your search. Please try again with different filters.
            </div>`;
            return;
        }
        update_results(response.data.results, response.data.current_page, response.data.num_pages, response.data.count);
        show_filters(filterTags);
    }).catch(function (error) {
        console.log(error);})



}


function clear_tag(key, value) {
    // let tag = document.querySelector(`.filter-tag:contains('${key} : ${value}')`);
    const url = new URL(window.location.href); // Get the current URL
    url.search = ''; // Remove the search (query parameters)
    window.history.replaceState({}, document.title, url.toString()); 

    console.log(key, value);


    let tag = document.querySelector(`.filter-tag[key="${key}"][value="${value}"]`);
    if (tag) {
        tag.remove();
    }
    let checkbox = document.querySelector(`input[name="${key}"][value="${value}"]`);
    if (checkbox) {
        checkbox.checked = false;
    }
    else{
        let text_element = document.querySelector(`input[name="${key}"]`);
        if (text_element) {
            text_element.value = "";
        }
    }

    update_cars_data();
}


function show_filters(filter_tags) {
    document.getElementById("filter-tags").innerHTML = "";


    Object.entries(filter_tags).forEach(([key, value]) => {
        if (Array.isArray(value) && value.length > 0) {
            console.log(value,"value")
            removeDuplicates(value, "name").forEach(item => {
                if (item.name) {
                    let tag = create_tag(key, item.id, item.name);
                    document.getElementById("filter-tags").insertAdjacentHTML("beforeend", tag);
                }
            });
        } else if (typeof value === "string" && value.trim() !== "") {
            let tag = create_tag(key, value, value);
            document.getElementById("filter-tags").insertAdjacentHTML("beforeend", tag);
        }
    });
}

function create_tag(key, value, name) {
    return `<div class="filter-tag" key="${key}" value="${value}">
                                <span>${name}</span>
                                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="cursor: pointer;" onclick="clear_tag('${key}', '${value}')">
                                    <path fill-rule="evenodd" clip-rule="evenodd" d="M6.99984 1.16666C3.774 1.16666 1.1665 3.77416 1.1665 7C1.1665 10.2258 3.774 12.8333 6.99984 12.8333C10.2257 12.8333 12.8332 10.2258 12.8332 7C12.8332 3.77416 10.2257 1.16666 6.99984 1.16666ZM9.9165 9.09416L9.094 9.91667L6.99984 7.8225L4.90567 9.91667L4.08317 9.09416L6.17734 7L4.08317 4.90583L4.90567 4.08333L6.99984 6.1775L9.094 4.08333L9.9165 4.90583L7.82234 7L9.9165 9.09416Z" fill="white"/>
                                </svg>
                            </div>`
}

function uncheck_all(e, props) {
    e?.stopPropagation?.();
    const {title, toggleId, triggerId, inputName} = props;
    document.querySelectorAll(`input[name=${inputName}]:checked`).forEach((checkbox) => {
        checkbox.click()
    });

    document.getElementById(triggerId).innerHTML = mobileFilterTemplateEngine(title, [], toggleId, triggerId, inputName);
}
function mobileFilterTemplateEngine(title, dataList, toggleId, triggerId, inputName){
    const toggleIdFromParams = `#${toggleId}`
    if (dataList && dataList.length > 0) {
        // Filled Filter State

        let props = {
            toggleId,
            triggerId,
            inputName,
            title
        }

        if (!inputName){
            return `
             <h2 class="accordion-header">
                 <button
                                                class="text-heading d-flex justify-content-between align-items-center"
                                                type="button"
                                                data-bs-toggle="modal"
                                                data-bs-target=${toggleIdFromParams}
                                        >
                                            <div class="d-flex flex-column align-items-start">
                                                <span class="text-secondary-color" style="font-size: 12px;">${title}</span>
                                                 <span class="text-primary-color font-medium" style="font-size: 18px;text-align: left;">${dataList.join(",")}</span>
                                            </div>
                                            <div></div>
                                        </button>                        
            </h2>
            `
        }

        return `
            <h2 class="accordion-header">
                 <button
                                                class="text-heading d-flex justify-content-between align-items-center"
                                                type="button"
                                                data-bs-toggle="modal"
                                                data-bs-target=${toggleIdFromParams}
                                        >
                                            <div class="d-flex flex-column align-items-start">
                                                <span class="text-secondary-color" style="font-size: 12px;">${title}</span>
                                                 <span class="text-primary-color font-medium" style="font-size: 18px;text-align: left;">${dataList.join(",")}</span>
                                            </div>
                                            <i class="bi bi-x-circle-fill text-secondary-color" style="font-size: 20px;cursor:pointer;" onclick='uncheck_all(event,${JSON.stringify(props)})'></i>
                                        </button>                        
            </h2>
        `
    }else {
        // Empty Filter State
        return `
            <h2 class="accordion-header">
                <a
                    class="text-heading text-secondary-color d-flex justify-content-between align-items-center"
                    type="button"
                    data-bs-toggle="modal"
                    data-bs-target=${toggleIdFromParams}
                >
                    <span>${title}</span>
                    <i class="bi bi-chevron-right text-secondary-color" style="font-size: 20px;"></i>
                </a>
            </h2>
        `
    }
}
function update_models() {
    // Clear the existing models
    const windowWidth = window.innerWidth

    if (windowWidth > 767){
        document.getElementById("models_form").innerHTML = "";
    }else{
        document.getElementById("models_form_mobile").innerHTML = "";
    }



    let selectedMakes = [];
    document.querySelectorAll('input[name="make"]:checked').forEach((checkbox) => {
        selectedMakes.push(checkbox.value);
    });
    selectedMakes = removeDuplicates(selectedMakes)

    const selectedMakeNames = []
    if (selectedMakes.length > 0){
        selectedMakes.forEach(selectedMake => {
            const currentElementNames = document.getElementById(`make_${selectedMake}`).getAttribute("name-attr")
            selectedMakeNames.push(currentElementNames)
        })
        if(windowWidth  <= 767){
            document.getElementById("filterMobileMakeTrigger").innerHTML = mobileFilterTemplateEngine("Vehicle Make", selectedMakeNames, "mobileFilterMake", "filterMobileMakeTrigger", "make")
        }
    }else{
        //empty make list
        if(windowWidth  <= 767){
            document.getElementById("filterMobileMakeTrigger").innerHTML = mobileFilterTemplateEngine("Vehicle Make", [], "mobileFilterMake", "filterMobileMakeTrigger", "make")
        }
    }

    // Send request to get models
    axios.get('/api/models-from-id/', {
        params: { makes: selectedMakes }
    })
    .then(function (response) {

        response.data.forEach(element => {
            var  option = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="model_${element.id}" name-attr=${element.name} name="model" value="${element.id}">
                    <label class="form-check-label text-start"  style="display: block;" name-attr=${element.name} for="model_${element.id}">
                        ${element.name}
                    </label>
                </div>
            `;

            if (windowWidth > 767){
                document.getElementById("models_form").insertAdjacentHTML("beforeend", option);
            }else{
                document.getElementById("models_form_mobile").insertAdjacentHTML("beforeend", option);
            }
        });

        if (!document.getElementById("model_apply")){
            if (windowWidth > 767){
                document.getElementById("models_form").insertAdjacentHTML("beforeend", `<button onclick="update_filters()" class="btn btn-danger mt-2" style="width: 100%;" id="model_apply">Apply</button>`);
            }
        }
        if (!document.getElementById("model_apply_mobile")){
            if (windowWidth <= 767){
                document.getElementById("models_form_mobile").insertAdjacentHTML("beforeend", `<button onclick="update_filters()" class="btn btn-danger mt-2" style="width: 100%;" id="model_apply_mobile">Apply</button>`);
            }
        }

        update_cars_data();
    })
    .catch(function (error) {
        console.log(error);
    });
    return true;
}

function update_results(data, current_page, total_pages, count) {
    document.getElementById("table_results").innerHTML = "";
    document.getElementById("table_results_mobile").innerHTML = "";
    const windowWidth = window.innerWidth

    let canvas = "";

    data.forEach(element => {
    let display_picture = '';
    if (element.all_media.length > 0 && element.all_media[0].img_url_from_api) { display_picture = element.all_media[0].img_url_from_api;}

        if (windowWidth <= 767){
            canvas += `
    <!--                    For Mobile:-->
                   <div class="d-flex d-md-none flex-column search-result-mobile-wrapper" style="gap:5px;">
                        <div class="d-flex align-items-start" style="gap:10px;">
                                <div class="" style="max-width: 120px;width: 100%;height: 100%;max-height: 98px;min-height: 98px;">
                         <a href="/normal-car-details/${element.id}" style="text-decoration: none;width: 100%;height: inherit;">
                                      
                                <img 
                                            src="${display_picture}"
                                            class="img-fluid" 
                                            alt="Car 1" 
                                            style="width: 100%;height: inherit;max-height: inherit;object-position: bottom;border-radius: 5px;min-height: inherit;object-fit: cover;"
                                        >
                                </a>

                                </div>
                                <div>
                                 <a href="/normal-car-details/${element.id}" style="text-decoration: none;width: 100%;height: inherit;">
                                    <p class="fs-6 text-start fw-bold m-0 text-primary-color " style="padding-bottom: 6px;">${element.make.name} ${element.model.name} ${element.year}</p>
                                    </a>
                                    <div class="d-flex align-items-center " style="gap:2px;">
                                       <p class="text-start text-color m-0" style="width:fit-content;font-size: 12px;">
                                            Price:
                                       </p>
                                        <p class="text-start text-primary-red m-0" style="width:fit-content;font-size: 12px;">
                                            $${(element.price - element.price_discount).toLocaleString()}
                                       </p>
                                    </div>
                                    <div class="d-flex align-items-center " style="gap:2px;">
                                       <p class="text-start text-color m-0" style="width:fit-content;font-size: 12px;">
                                            Engine:
                                       </p>
                                        <p class="text-start text-primary-red m-0" style="width:fit-content;font-size: 12px;">
                                            3.7L
                                       </p>
                                    </div>
                                    <div class="d-flex align-items-center " style="gap:2px;">
                                       <p class="text-start text-color m-0" style="width:fit-content;font-size: 12px;">
                                            Odometer:
                                       </p>
                                        <p class="text-start text-primary-red m-0" style="width:fit-content;font-size: 12px;">
                                          ${element.odometer} mi
                                       </p>
                                    </div>
                                  
                                 
                                </div>
                        </div> 
                    <div class="accordion acc-table" id="carDetailsAccordion_${element.id}">
                                <div class="accordion-item-table">
                                    <h2 class="accordion-header-table" id="heading${element.id}">                                    
                                        <button class="accordion-button-table" onclick="change_accordion_text('accordian_btn_${element.id}')" id="accordian_btn_${element.id}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${element.id}" aria-expanded="false" aria-controls="collapse${element.id}">
                                            <span class="toggle-text">More Details</span>
                                        </button>
                                    </h2>
                                    <div id="collapse${element.id}" class="accordion-collapse collapse detail-accordion-collapse" aria-labelledby="heading${element.id}" data-bs-parent="#carDetailsAccordion_${element.id}">
                                        <div class="accordion-body-table">
                                            <div class="text-center d-flex flex-wrap" style="gap:12px;">
                                                <div class="d-flex flex-column gap-0.5 text-left">
                                                    <span class="text-color text-sm">
                                                        Body Style:
                                                    </span> 
                                                    <span class="detail-item text-primary-color">
                                                        ${element.body_style.name_en}
                                                    </span>
                                                </div>
                                                <div class="d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Fuel Type:</span> <span class="detail-item text-primary-color">${element.fuel.name_en} </span></div>
                                                <div class="d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Transmission:</span> <span class="detail-item text-primary-color"> ${element.transmission.name_en} </span></div>
                                                <div class="d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Drive:</span> <span class="detail-item text-primary-color">${element.drive.name_en}</span></div>
                                                <div class="d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Color:</span> <span class="detail-item text-primary-color"> ${element.color.name_en} </span></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>                                  
                  </div>           
                        `
        }else{
            canvas += `
    <!--                    For Desktop-->
                   <div class="row g-4 d-none d-md-block">
                               <div class="row g-4">
                                <div class="col-12 col-md-2 " style="margin-top: 20px !important;">
                                    <div class="" style="max-width: 100%;width: 100%;height: 100%;max-height: 110px;">
                                        <a href="/normal-car-details/${element.id}" style="text-decoration: none;width: 100%;height: inherit;">
                                            <img 
                                                src="${display_picture}"
                                                class="img-fluid" 
                                                alt="Car 1" 
                                                style="width: 100%;height: inherit;object-fit: cover;object-position: bottom;"
                                                >
                                        </a>
                                    </div>
                                </div>
                                <div class="col-12 col-md-3 text-left" style="margin-top: 20px !important;">
                                    <a href="/normal-car-details/${element.id}" style="text-decoration: none;">
                                    <p class="fs-6 text-start fw-bold m-0 text-primary-color ">${element.make.name} ${element.model.name} ${element.year}</p>
                                    </a>
                                    </div>
                                <div class="col-12 col-md-2 text-left text-sm d-flex flex-column align-items-start" style="gap:4px;margin-top: 20px !important;">                                
                                  
                                    <div class="d-flex align-items-center"  style="gap:2px;padding-bottom: 5px;">
                                       <span class="fw-bold">Power:</span>  
                                        <span >${element.fuel.id === 3 ?`${element.motor_power} ${element.motor_power_unit || ""}` : `${element.engine_power} ${element.engine_power_unit || ""}`}</span>
                                    </div>
                                    <div class="d-flex align-items-center"  style="gap:2px;">
                                       <span class="fw-bold">${element.fuel.id === 3 ? "Battery:" : "Engine:"}</span>  
                                         <span >${element.fuel.id === 3 ? `${element.battery_range}` : `${element.engine_type}`}</span>
                                    </div>
                                   
                                 </div>
                                <div class="col-12 col-md-2 text-left text-sm" style="margin-top: 20px !important;">      
                                    <span>${element.odometer} mi</span> 
                                </div>
                               
                                <div class="col-12 col-md-3 d-none d-sm-flex flex-column text-left text-sm" style="gap: 4px;margin-top: 20px !important;">
                                    
                                    <div class="d-flex align-items-center" style="gap:2px;padding-bottom: 5px;">
                                        <span class="fw-bold">Price:</span> 
                                        <span>$${(element.price - element.price_discount).toLocaleString()}</span>
                                    </div>
                                    <div class="d-flex align-items-center"  style="gap:2px;">
                                        <span class="fw-bold">Location:</span>
                                        <span>${element.country.name}</span>
                                     </div>
                                    <a href="/normal-car-details/${element.id}" style="text-decoration: none;">
                                        <button class="btn btn-danger details-button font-medium text-sm d-flex align-items-center justify-content-center" style="width: 100%;max-width:95px;max-height: 28px;margin-top: 20px;margin-left: auto;">
                                            Details
                                        </button>
                                    </a>
                                </div>
                            </div>
                            
                            <div class="accordion acc-table" id="carDetailsAccordion_${element.id}">
                                <div class="accordion-item-table">
                                    <h2 class="accordion-header-table" id="heading${element.id}">                                    
                                        <button class="accordion-button-table" onclick="change_accordion_text('accordian_btn_${element.id}')" id="accordian_btn_${element.id}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${element.id}" aria-expanded="false" aria-controls="collapse${element.id}">
                                            <span class="toggle-text">More Details</span>
                                        </button>
                                    </h2>
                                    <div id="collapse${element.id}" class="accordion-collapse collapse detail-accordion-collapse" aria-labelledby="heading${element.id}" data-bs-parent="#carDetailsAccordion_${element.id}">
                                        <div class="accordion-body-table">
                                            <div class="row text-center justify-content-between">
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left">
                                                    <span class="text-color text-sm">
                                                        Body Style:
                                                    </span> 
                                                    <span class="detail-item text-primary-color">
                                                        ${element.body_style.name_en}
                                                    </span>
                                                </div>
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Fuel Type:</span> <span class="detail-item text-primary-color">${element.fuel.name_en} </span></div>
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Transmission:</span> <span class="detail-item text-primary-color"> ${element.transmission.name_en} </span></div>
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Drive:</span> <span class="detail-item text-primary-color">${element.drive.name_en}</span></div>
                                                <div class="col-md-2 d-flex flex-column gap-0.5 text-left"><span class="text-color text-sm">Color:</span> <span class="detail-item text-primary-color"> ${element.color.name_en} </span></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>                                  
                        </div>
                        `
        }
    });
    document.getElementById("table_results").innerHTML = canvas;
    document.getElementById("table_results_mobile").innerHTML = canvas;


    if (windowWidth <= 767){
        document.getElementById("total-page-view").innerHTML = `${count} Listings`;
    }else{
        document.getElementById("total-page-view").innerHTML = `Showing page ${current_page} out of ${total_pages} total pages`;
    }

    let pagination_buttons = "";
    document.getElementById("search-pagination").innerHTML = pagination_buttons;

    for (let i = 1; i <= total_pages; i++) {
        if (i === current_page) {
            pagination_buttons += `<a class="page-link text-white rounded" style="background: red"><li class="page-item ">${i}</li></a>`;
        } else {
            pagination_buttons += `<a class="page-link text-danger rounded" onclick="update_cars_data( ${i} )"><li class="page-item">${i}</li></a>`;
        }        
    }

    document.getElementById("search-pagination").innerHTML = pagination_buttons;

}


document.querySelector('#open-filter-sidebar').addEventListener('click', function(e)  {
    //Open Filter
    document.getElementById("main-filter-sidebar").classList.remove("hide-filter-sidebar")
    document.getElementById("collapsed-filter-sidebar").classList.add("d-md-none")
    document.getElementById("collapsed-filter-sidebar").classList.remove("d-md-flex")
    document.getElementById("results-section").classList.add("col-md-9")
    document.getElementById("results-section").classList.remove("col-md-11")
});

document.querySelector('#close-filter-sidebar').addEventListener('click', function(e)  {
    //Close Filter
    document.getElementById("main-filter-sidebar").classList.add("hide-filter-sidebar")
    document.getElementById("collapsed-filter-sidebar").classList.remove("d-md-none")
    document.getElementById("collapsed-filter-sidebar").classList.add("d-md-flex")
    document.getElementById("results-section").classList.remove("col-md-9")
    document.getElementById("results-section").classList.add("col-md-11")
});