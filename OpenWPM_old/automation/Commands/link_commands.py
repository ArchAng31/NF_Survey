# A Module for extracting links and images from inside a site
# Also extracts links and images from all iframes
from ..SocketInterface import clientsocket



def save_links(db_socket_address, crawl_url, crawl_id, resource_urls_list, page_url):
    # Send queries to DataAggregator
    sock = clientsocket()
    sock.connect(*db_socket_address)
    for item in resource_urls_list:
        if item[0] and item[0] != "":
            query = (("INSERT INTO Resource_Loads_Static (crawl_id, crawl_url, content_type, \
            resource_url, isInIFrame, parser_results, window_url, request_origin) VALUES (?,?,?,?,?,?,?,?)",
                    (crawl_id, crawl_url, item[1], item[0], item[2], "Not Checked", page_url, item[3])))
            sock.send(query)
    sock.close()


def extract_links(crawl_id, crawl_url, driver, browser_settings, db_socket_address):
    '''
        Extract all of the links on a given page
    '''

    resource_list = list()

    item_list = driver.find_elements_by_tag_name('a')
    for item in item_list:
        try:
            temp = [item.get_attribute('href'), 'A TAG', ' ', driver.current_url]
            resource_list.append(temp)
        except:
            continue

    img_list = driver.find_elements_by_tag_name('img')
    for item in img_list:
        try:
            temp = [item.get_attribute('src'), 'IMAGE', ' ', driver.current_url]
            resource_list.append(temp)
        except:
            continue

    object_list = driver.find_elements_by_tag_name('object')
    for item in object_list:
        try:
            temp = [item.get_attribute('data'), 'OBJECT', ' ', driver.current_url]
            resource_list.append(temp)
        except:
            continue

    link_list = driver.find_elements_by_tag_name('link')
    for item in link_list:
        try:
            item_type = 'LINK-' + item.get_attribute('rel')
            temp = [item.get_attribute('href'), item_type, ' ', driver.current_url]
            resource_list.append(temp)
        except:
            continue

    script_list = driver.find_elements_by_tag_name('script')
    for item in script_list:
        try:
            temp = [item.get_attribute('src'), 'SCRIPT', ' ', driver.current_url]
            resource_list.append(temp)
        except:
            continue

    frames = driver.find_elements_by_tag_name('iframe')
    for frame in frames:
        driver.switch_to_default_content()
        #must switch back to default content to access iframe attributes
        temp = [frame.get_attribute('src'), 'SUBDOCUMENT', ' ', driver.current_url]
        resource_list.append(temp)
        driver.switch_to_frame(frame)
        item_list = driver.find_elements_by_tag_name('a')
        for item in item_list:
            try:
                temp = [item.get_attribute('href'), 'A TAG', 'True', driver.current_url]
                resource_list.append(temp)
            except:
                continue

        img_list = driver.find_elements_by_tag_name('img')
        for item in img_list:
            try:
                temp = [item.get_attribute('src'), 'IMAGE', 'True', driver.current_url]
                resource_list.append(temp)
            except:
                continue

        link_list = driver.find_elements_by_tag_name('link')
        for item in link_list:
            try:
                item_type = 'LINK-' + item.get_attribute('rel')
                temp = [item.get_attribute('href'), item_type, 'True', driver.current_url]
                resource_list.append(temp)
            except:
                continue

        object_list = driver.find_elements_by_tag_name('object')
        for item in object_list:
            try:
                temp = [item.get_attribute('data'), 'OBJECT', 'True', driver.current_url]
                resource_list.append(temp)
            except:
                continue

        script_list = driver.find_elements_by_tag_name('script')
        for item in script_list:
            try:
                temp = [item.get_attribute('src'), 'SCRIPT', 'True', driver.current_url]
                resource_list.append(temp)
            except:
                continue

    driver.switch_to_default_content()
    if resource_list:
        save_links(db_socket_address, crawl_url, crawl_id, resource_list, driver.current_url)